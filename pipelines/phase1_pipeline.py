"""
Phase 1 ETL Pipeline for JusticeGraph.

Orchestrates the complete data collection, parsing, normalization,
validation, and loading workflow using Prefect.
"""

import sys
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import List, Optional
import time

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.logging_utils import get_logger, log_pipeline_stage
from utils.db_utils import DatabaseManager
from utils.io_utils import get_data_path

logger = get_logger('pipeline')

# Try to import Prefect, but make it optional
try:
    from prefect import flow, task  # type: ignore[attr-defined]
    PREFECT_AVAILABLE = True
except ImportError:
    logger.warning("Prefect not available. Running without workflow orchestration.")
    PREFECT_AVAILABLE = False
    # Create dummy decorators
    def flow(func=None, **kwargs):  # type: ignore[misc]
        def decorator(f):  # type: ignore[misc]
            return f
        return decorator(func) if func else decorator
    def task(func=None, **kwargs):  # type: ignore[misc]
        def decorator(f):  # type: ignore[misc]
            return f
        return decorator(func) if func else decorator


@task
def ingest_cause_lists(
    court_code: str,
    base_url: str,
    start_date: date,
    end_date: date
) -> List[str]:
    """
    Task to ingest cause lists for a date range.
    
    Args:
        court_code: Court code
        base_url: Base URL of court website
        start_date: Start date
        end_date: End date
    
    Returns:
        List of file paths for ingested cause lists
    """
    start_time = time.time()
    logger.info(f"Starting cause list ingestion for {court_code}")
    
    try:
        from ingest.cause_list_ingest import CauseListScraper
        
        scraper = CauseListScraper(court_code, base_url)
        file_paths = scraper.fetch_cause_lists_range(start_date, end_date, delay_seconds=2.0)
        
        duration = time.time() - start_time
        log_pipeline_stage(
            logger,
            'ingest_cause_lists',
            'completed',
            input_count=0,
            output_count=len(file_paths),
            duration_seconds=duration
        )
        
        return file_paths
        
    except Exception as e:
        logger.exception(f"Error in cause list ingestion: {e}")
        log_pipeline_stage(
            logger,
            'ingest_cause_lists',
            'failed',
            duration_seconds=time.time() - start_time
        )
        return []


@task
def parse_cause_lists(file_paths: List[str]) -> List[str]:
    """
    Task to parse ingested cause lists.
    
    Args:
        file_paths: List of raw HTML file paths
    
    Returns:
        List of parsed CSV file paths
    """
    start_time = time.time()
    logger.info(f"Starting cause list parsing for {len(file_paths)} files")
    
    try:
        from parse.parse_cause_list import CauseListParser
        
        parser = CauseListParser()
        output_files = []
        
        for file_path in file_paths:
            try:
                output_file = parser.parse_and_save(file_path)
                output_files.append(output_file)
            except Exception as e:
                logger.error(f"Error parsing {file_path}: {e}")
        
        duration = time.time() - start_time
        log_pipeline_stage(
            logger,
            'parse_cause_lists',
            'completed',
            input_count=len(file_paths),
            output_count=len(output_files),
            duration_seconds=duration
        )
        
        return output_files
        
    except Exception as e:
        logger.exception(f"Error in cause list parsing: {e}")
        log_pipeline_stage(
            logger,
            'parse_cause_lists',
            'failed',
            duration_seconds=time.time() - start_time
        )
        return []


@task
def normalize_data(input_files: List[str]) -> List[str]:
    """
    Task to normalize parsed data.
    
    Args:
        input_files: List of parsed CSV files
    
    Returns:
        List of normalized file paths
    """
    start_time = time.time()
    logger.info(f"Starting data normalization for {len(input_files)} files")
    
    try:
        import pandas as pd
        from normalize.clean_text_utils import (
            normalize_case_number,
            clean_name,
            remove_honorifics
        )
        
        output_files = []
        gold_dir = get_data_path('gold')
        
        for input_file in input_files:
            try:
                # Load data
                df = pd.read_csv(input_file)
                
                # Normalize case numbers
                if 'case_number' in df.columns:
                    df['normalized_case_number'] = df['case_number'].apply(
                        lambda x: normalize_case_number(str(x)) if pd.notna(x) else x
                    )
                
                # Clean names
                for col in ['petitioner', 'respondent', 'petitioner_advocate', 'respondent_advocate']:
                    if col in df.columns:
                        df[col] = df[col].apply(
                            lambda x: clean_name(str(x)) if pd.notna(x) else x
                        )
                
                # Save to gold layer
                output_file = gold_dir / Path(input_file).name
                df.to_csv(output_file, index=False)
                output_files.append(str(output_file))
                
            except Exception as e:
                logger.error(f"Error normalizing {input_file}: {e}")
        
        duration = time.time() - start_time
        log_pipeline_stage(
            logger,
            'normalize_data',
            'completed',
            input_count=len(input_files),
            output_count=len(output_files),
            duration_seconds=duration
        )
        
        return output_files
        
    except Exception as e:
        logger.exception(f"Error in data normalization: {e}")
        log_pipeline_stage(
            logger,
            'normalize_data',
            'failed',
            duration_seconds=time.time() - start_time
        )
        return []


@task
def validate_data(input_files: List[str]) -> bool:
    """
    Task to validate normalized data.
    
    Args:
        input_files: List of normalized CSV files
    
    Returns:
        True if validation passed, False otherwise
    """
    start_time = time.time()
    logger.info(f"Starting data validation for {len(input_files)} files")
    
    try:
        import pandas as pd
        
        all_valid = True
        
        for input_file in input_files:
            try:
                df = pd.read_csv(input_file)
                
                # Check for required fields
                required_fields = ['case_number', 'court_code', 'list_date']
                missing_fields = [f for f in required_fields if f not in df.columns]
                
                if missing_fields:
                    logger.warning(f"Missing required fields in {input_file}: {missing_fields}")
                    all_valid = False
                    continue
                
                # Check for null values in critical fields
                null_counts = df[required_fields].isnull().sum()
                if null_counts.any():
                    logger.warning(f"Null values found in {input_file}: {null_counts.to_dict()}")
                    all_valid = False
                
                # Check for duplicates
                duplicates = df.duplicated(subset=['case_number', 'list_date']).sum()
                if duplicates > 0:
                    logger.warning(f"Found {duplicates} duplicate records in {input_file}")
                
            except Exception as e:
                logger.error(f"Error validating {input_file}: {e}")
                all_valid = False
        
        duration = time.time() - start_time
        log_pipeline_stage(
            logger,
            'validate_data',
            'completed' if all_valid else 'completed_with_warnings',
            input_count=len(input_files),
            duration_seconds=duration
        )
        
        return all_valid
        
    except Exception as e:
        logger.exception(f"Error in data validation: {e}")
        log_pipeline_stage(
            logger,
            'validate_data',
            'failed',
            duration_seconds=time.time() - start_time
        )
        return False


@task
def load_to_database(input_files: List[str]) -> int:
    """
    Task to load normalized data into database.
    
    Args:
        input_files: List of normalized CSV files
    
    Returns:
        Number of records loaded
    """
    start_time = time.time()
    logger.info(f"Starting database load for {len(input_files)} files")
    
    try:
        import pandas as pd
        from models.data_models import CauseList
        
        db = DatabaseManager()
        total_records = 0
        
        for input_file in input_files:
            try:
                df = pd.read_csv(input_file)
                
                # Convert DataFrame rows to CauseList objects
                # This is a simplified example - actual implementation would be more robust
                records = []
                for _, row in df.iterrows():
                    list_date_str = row.get('list_date')
                    list_date_obj = pd.to_datetime(list_date_str).date() if list_date_str else None
                    cause_list = CauseList(
                        court_code=row.get('court_code'),
                        list_date=list_date_obj,
                        case_number=row.get('case_number'),
                        case_title=row.get('case_title'),
                        hearing_time=row.get('hearing_time'),
                        purpose=row.get('purpose')
                    )
                    records.append(cause_list)
                
                # Insert records
                count = db.insert_many(records)
                total_records += count
                logger.info(f"Loaded {count} records from {input_file}")
                
            except Exception as e:
                logger.error(f"Error loading {input_file}: {e}")
        
        duration = time.time() - start_time
        log_pipeline_stage(
            logger,
            'load_to_database',
            'completed',
            input_count=len(input_files),
            output_count=total_records,
            duration_seconds=duration
        )
        
        return total_records
        
    except Exception as e:
        logger.exception(f"Error loading to database: {e}")
        log_pipeline_stage(
            logger,
            'load_to_database',
            'failed',
            duration_seconds=time.time() - start_time
        )
        return 0


@flow(name="JusticeGraph Phase 1 Pipeline")
def phase1_pipeline(
    court_code: str,
    base_url: str,
    start_date: date,
    end_date: date
) -> dict:
    """
    Complete Phase 1 ETL pipeline.
    
    Args:
        court_code: Court code to process
        base_url: Base URL of court website
        start_date: Start date for data collection
        end_date: End date for data collection
    
    Returns:
        Dictionary with pipeline execution summary
    
    Example:
        >>> from datetime import date
        >>> result = phase1_pipeline(
        ...     'DL-HC',
        ...     'https://delhihighcourt.nic.in',
        ...     date(2023, 11, 1),
        ...     date(2023, 11, 7)
        ... )
    """
    pipeline_start = time.time()
    logger.info(f"Starting Phase 1 pipeline for {court_code} from {start_date} to {end_date}")
    
    try:
        # Step 1: Ingest
        raw_files = ingest_cause_lists(court_code, base_url, start_date, end_date)
        logger.info(f"Ingested {len(raw_files)} cause lists")
        
        if not raw_files:
            logger.warning("No files ingested, stopping pipeline")
            return {'status': 'failed', 'reason': 'No files ingested'}
        
        # Step 2: Parse
        parsed_files = parse_cause_lists(raw_files)
        logger.info(f"Parsed {len(parsed_files)} cause lists")
        
        if not parsed_files:
            logger.warning("No files parsed, stopping pipeline")
            return {'status': 'failed', 'reason': 'No files parsed'}
        
        # Step 3: Normalize
        normalized_files = normalize_data(parsed_files)
        logger.info(f"Normalized {len(normalized_files)} files")
        
        # Step 4: Validate
        validation_passed = validate_data(normalized_files)
        logger.info(f"Validation {'passed' if validation_passed else 'failed'}")
        
        # Step 5: Load to database
        records_loaded = load_to_database(normalized_files)
        logger.info(f"Loaded {records_loaded} records to database")
        
        pipeline_duration = time.time() - pipeline_start
        
        result = {
            'status': 'completed',
            'court_code': court_code,
            'date_range': f"{start_date} to {end_date}",
            'files_ingested': len(raw_files),
            'files_parsed': len(parsed_files),
            'files_normalized': len(normalized_files),
            'validation_passed': validation_passed,
            'records_loaded': records_loaded,
            'duration_seconds': round(pipeline_duration, 2)
        }
        
        logger.info(f"Pipeline completed successfully: {result}")
        return result
        
    except Exception as e:
        logger.exception(f"Pipeline failed: {e}")
        return {
            'status': 'failed',
            'error': str(e),
            'duration_seconds': round(time.time() - pipeline_start, 2)
        }


def run_phase1_pipeline(
    court_code: str = 'DL-HC',
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Convenience function to run the pipeline with string dates.
    
    Args:
        court_code: Court code
        start_date: Start date as string (YYYY-MM-DD)
        end_date: End date as string (YYYY-MM-DD)
    
    Example:
        >>> run_phase1_pipeline('DL-HC', '2023-11-01', '2023-11-07')
    """
    if not start_date:
        start_date = (date.today() - timedelta(days=7)).isoformat()
    if not end_date:
        end_date = date.today().isoformat()
    
    start = datetime.fromisoformat(start_date).date()
    end = datetime.fromisoformat(end_date).date()
    
    # Map court codes to base URLs (should be in config)
    court_urls = {
        'DL-HC': 'https://delhihighcourt.nic.in',
        'MH-HC': 'https://bombayhighcourt.nic.in',
        'SC-INDIA': 'https://main.sci.gov.in'
    }
    
    base_url = court_urls.get(court_code, '')
    
    result = phase1_pipeline(court_code, base_url, start, end)
    print(f"\nPipeline Result: {result}")
    return result


if __name__ == "__main__":
    """
    Run the pipeline from command line.
    """
    import sys
    
    if len(sys.argv) > 1:
        court_code = sys.argv[1]
        start_date = sys.argv[2] if len(sys.argv) > 2 else None
        end_date = sys.argv[3] if len(sys.argv) > 3 else None
        
        run_phase1_pipeline(court_code, start_date, end_date)
    else:
        print("Usage: python phase1_pipeline.py COURT_CODE [START_DATE] [END_DATE]")
        print("Example: python phase1_pipeline.py DL-HC 2023-11-01 2023-11-07")
