"""
Case Status Ingestion Module for JusticeGraph.

Scrapes individual case status information from court websites and saves
them to the bronze layer for processing.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from bs4 import BeautifulSoup
import re

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.http_utils import fetch_url, get_page_with_post
from utils.io_utils import save_with_metadata, get_data_path, generate_filename
from utils.logging_utils import get_logger, log_scraper_activity

logger = get_logger('ingest')


class CaseStatusScraper:
    """
    Scraper for individual case status information.
    
    Fetches detailed case information including case history, parties,
    hearings, and current status from court websites.
    """
    
    def __init__(self, court_code: str, base_url: str):
        """
        Initialize the case status scraper.
        
        Args:
            court_code: Standardized court code (e.g., 'DL-HC')
            base_url: Base URL of the court's case status portal
        
        Example:
            >>> scraper = CaseStatusScraper('DL-HC', 'https://delhihighcourt.nic.in')
            >>> case_data = scraper.fetch_case_status('CRL.A/123/2023')
        """
        self.court_code = court_code
        self.base_url = base_url
        self.bronze_dir = get_data_path('bronze')
        
        logger.info(f"Initialized CaseStatusScraper for {court_code}")
    
    def fetch_case_status(
        self,
        case_number: str,
        case_type: Optional[str] = None,
        case_year: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch detailed status for a specific case.
        
        Args:
            case_number: Full case number or case number without type/year
            case_type: Case type (if providing parts separately)
            case_year: Case year (if providing parts separately)
        
        Returns:
            Dictionary containing case data and file path, or None if failed
        
        Example:
            >>> scraper = CaseStatusScraper('DL-HC', 'https://delhihighcourt.nic.in')
            >>> data = scraper.fetch_case_status('CRL.A/123/2023')
        """
        try:
            # Parse case number if provided as full string
            if not case_type or not case_year:
                parsed = self._parse_case_number(case_number)
                if parsed:
                    case_type = parsed.get('case_type', case_type)
                    case_year = parsed.get('case_year', case_year)
                    case_number = parsed.get('case_number', case_number)
            
            # Build search URL or form data
            url = f"{self.base_url}/case_status"
            
            form_data = {
                'case_type': case_type or '',
                'case_number': case_number,
                'case_year': case_year or '',
                'court_code': self.court_code
            }
            
            logger.info(f"Fetching case status for {case_type}/{case_number}/{case_year}")
            
            # Fetch the page
            response = get_page_with_post(url, form_data, timeout=60)
            
            if not response:
                log_scraper_activity(
                    logger,
                    'case_status_ingest',
                    url,
                    'failed',
                    errors=['Failed to fetch page']
                )
                return None
            
            # Generate filename
            safe_case_num = re.sub(r'[^\w\-]', '_', case_number)
            filename = generate_filename(
                'case_status',
                'html',
                include_timestamp=True,
                additional_parts=[self.court_code, safe_case_num]
            )
            
            # Save to bronze layer
            file_path = self.bronze_dir / filename
            
            # Prepare metadata
            metadata = {
                'court_code': self.court_code,
                'case_number': case_number,
                'case_type': case_type,
                'case_year': case_year,
                'source_url': url,
                'fetch_timestamp': datetime.utcnow().isoformat(),
                'content_length': len(response.text),
                'html_file': filename
            }
            
            # Save with metadata
            metadata_file = file_path.with_suffix('.json')
            save_with_metadata(
                {'html_content': response.text},
                metadata_file,
                url,
                metadata
            )
            
            log_scraper_activity(
                logger,
                'case_status_ingest',
                url,
                'success',
                record_count=1,
                case_number=f"{case_type}/{case_number}/{case_year}"
            )
            
            return {
                'file_path': str(file_path),
                'metadata_path': str(metadata_file),
                'case_number': case_number,
                'metadata': metadata
            }
            
        except Exception as e:
            logger.exception(f"Error fetching case status: {e}")
            log_scraper_activity(
                logger,
                'case_status_ingest',
                self.base_url,
                'failed',
                errors=[str(e)]
            )
            return None
    
    def fetch_multiple_cases(
        self,
        case_numbers: List[str],
        delay_seconds: float = 2.0
    ) -> List[Dict[str, Any]]:
        """
        Fetch status for multiple cases.
        
        Args:
            case_numbers: List of case numbers to fetch
            delay_seconds: Delay between requests
        
        Returns:
            List of dictionaries containing case data
        
        Example:
            >>> scraper = CaseStatusScraper('DL-HC', 'https://delhihighcourt.nic.in')
            >>> cases = scraper.fetch_multiple_cases([
            ...     'CRL.A/123/2023',
            ...     'CRL.A/124/2023',
            ...     'CRL.A/125/2023'
            ... ])
        """
        import time
        
        results = []
        
        for i, case_number in enumerate(case_numbers):
            logger.info(f"Fetching case {i+1}/{len(case_numbers)}: {case_number}")
            
            result = self.fetch_case_status(case_number)
            if result:
                results.append(result)
            
            # Rate limiting
            if i < len(case_numbers) - 1:
                time.sleep(delay_seconds)
        
        logger.info(f"Successfully fetched {len(results)}/{len(case_numbers)} cases")
        return results
    
    def _parse_case_number(self, case_number: str) -> Optional[Dict[str, str]]:
        """
        Parse a case number string into components.
        
        Attempts to extract case type, number, and year from formats like:
        - CRL.A/123/2023
        - CRL.A. 123 of 2023
        - CRIMINAL APPEAL NO. 123/2023
        
        Args:
            case_number: Full case number string
        
        Returns:
            Dictionary with case_type, case_number, and case_year
        
        Example:
            >>> scraper = CaseStatusScraper('DL-HC', 'url')
            >>> scraper._parse_case_number('CRL.A/123/2023')
            {'case_type': 'CRL.A', 'case_number': '123', 'case_year': '2023'}
        """
        # Try different patterns
        patterns = [
            r'([A-Z\.]+)[/\s]+(\d+)[/\s]+(\d{4})',  # CRL.A/123/2023
            r'([A-Z\s]+)\s+NO\.\s*(\d+)[/\s]+(\d{4})',  # CRIMINAL APPEAL NO. 123/2023
            r'([A-Z\.]+)\.\s*(\d+)\s+of\s+(\d{4})',  # CRL.A. 123 of 2023
        ]
        
        for pattern in patterns:
            match = re.search(pattern, case_number, re.IGNORECASE)
            if match:
                return {
                    'case_type': match.group(1).strip().upper(),
                    'case_number': match.group(2),
                    'case_year': match.group(3)
                }
        
        logger.warning(f"Could not parse case number: {case_number}")
        return None


def fetch_ecourts_case_status(
    state_code: str,
    district_code: str,
    case_number: str,
    case_type: str,
    case_year: str
) -> Optional[Dict[str, Any]]:
    """
    Fetch case status from eCourts portal (template function).
    
    Args:
        state_code: State code
        district_code: District code
        case_number: Case number
        case_type: Case type
        case_year: Case year
    
    Returns:
        Dictionary with case data, or None if failed
    
    Example:
        >>> data = fetch_ecourts_case_status('DL', '01', '123', 'CRL.A', '2023')
    """
    base_url = "https://services.ecourts.gov.in/ecourtindia_v6/"
    court_code = f"{state_code}-{district_code}"
    
    scraper = CaseStatusScraper(court_code, base_url)
    return scraper.fetch_case_status(case_number, case_type, case_year)


def batch_fetch_from_cause_list(
    cause_list_data: List[Dict[str, str]],
    court_code: str,
    base_url: str,
    delay_seconds: float = 2.0
) -> List[Dict[str, Any]]:
    """
    Fetch case status for all cases from a parsed cause list.
    
    Args:
        cause_list_data: List of dictionaries with case numbers from cause list
        court_code: Court code
        base_url: Base URL of the court website
        delay_seconds: Delay between requests
    
    Returns:
        List of case data dictionaries
    
    Example:
        >>> cause_list = [
        ...     {'case_number': 'CRL.A/123/2023'},
        ...     {'case_number': 'CRL.A/124/2023'}
        ... ]
        >>> cases = batch_fetch_from_cause_list(
        ...     cause_list,
        ...     'DL-HC',
        ...     'https://delhihighcourt.nic.in'
        ... )
    """
    scraper = CaseStatusScraper(court_code, base_url)
    
    case_numbers = [item['case_number'] for item in cause_list_data if 'case_number' in item]
    
    return scraper.fetch_multiple_cases(case_numbers, delay_seconds)


if __name__ == "__main__":
    """
    Example usage of the case status scraper.
    """
    # Example: Fetch case status from Delhi High Court
    scraper = CaseStatusScraper(
        court_code='DL-HC',
        base_url='https://delhihighcourt.nic.in'
    )
    
    # Fetch single case
    case_data = scraper.fetch_case_status('CRL.A/123/2023')
    
    if case_data:
        print(f"Successfully fetched case: {case_data['case_number']}")
        print(f"Saved to: {case_data['file_path']}")
    else:
        print("Failed to fetch case")
    
    # Fetch multiple cases
    case_numbers = [
        'CRL.A/123/2023',
        'CRL.A/124/2023',
        'CRL.A/125/2023'
    ]
    
    results = scraper.fetch_multiple_cases(case_numbers, delay_seconds=3.0)
    print(f"Fetched {len(results)} out of {len(case_numbers)} cases")
