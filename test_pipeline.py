"""
Test script for JusticeGraph Phase 1 Pipeline.

Run this script to verify the complete ETL pipeline with sample data.
"""

import sys
from pathlib import Path
from datetime import date, timedelta

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))

from utils.logging_utils import setup_logger
from utils.db_utils import DatabaseManager
from utils.io_utils import get_data_path, save_text
import logging

# Set up logger
logger = setup_logger('test', 'test_pipeline.log', level=logging.INFO, json_format=False)


def test_database_setup():
    """Test database connection and table creation."""
    logger.info("=" * 60)
    logger.info("Testing Database Setup")
    logger.info("=" * 60)
    
    try:
        db = DatabaseManager()
        logger.info("✓ Database manager initialized")
        
        # Create tables
        db.create_tables()
        logger.info("✓ Database tables created successfully")
        
        # Test connection
        from models.data_models import Court
        count = db.get_table_count(Court)
        logger.info(f"✓ Database connection verified (Courts table has {count} records)")
        
        return True
    except Exception as e:
        logger.error(f"✗ Database setup failed: {e}")
        return False


def test_data_models():
    """Test data model creation and serialization."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Data Models")
    logger.info("=" * 60)
    
    try:
        from models.data_models import Court, Judge, Case, CaseType, CaseStatus
        from datetime import date
        
        # Create a test court
        court = Court(
            court_name="Test High Court",
            court_code="TEST-HC",
            court_type="High Court",
            state="Test State"
        )
        
        court_dict = court.to_dict()
        logger.info(f"✓ Court model created: {court.court_name}")
        logger.info(f"  Serialization: {court_dict['court_name']}")
        
        # Create a test case
        test_case = Case(
            case_number="TEST/123/2023",
            normalized_case_number="TEST/123/2023",
            case_type=CaseType.CIVIL,
            case_status=CaseStatus.PENDING,
            filing_date=date(2023, 1, 15),
            court_id=1,
            petitioner="Test Petitioner",
            respondent="Test Respondent"
        )
        
        case_dict = test_case.to_dict()
        logger.info(f"✓ Case model created: {test_case.case_number}")
        logger.info(f"  Case type: {case_dict['case_type']}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Data model test failed: {e}")
        return False


def test_utilities():
    """Test utility functions."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Utility Functions")
    logger.info("=" * 60)
    
    try:
        # Test text cleaning
        from normalize.clean_text_utils import (
            normalize_case_number,
            clean_name,
            remove_honorifics
        )
        
        # Test case number normalization
        case_num = normalize_case_number("CRL. A. 123 of 2023")
        assert "CRL.A/123/2023" == case_num, f"Expected 'CRL.A/123/2023', got '{case_num}'"
        logger.info(f"✓ Case number normalization: 'CRL. A. 123 of 2023' → '{case_num}'")
        
        # Test name cleaning
        name = clean_name("  Hon'ble Mr. Justice JOHN DOE  ")
        assert "John Doe" == name, f"Expected 'John Doe', got '{name}'"
        logger.info(f"✓ Name cleaning: 'Hon'ble Mr. Justice JOHN DOE' → '{name}'")
        
        # Test honorific removal
        name2 = remove_honorifics("Hon'ble Justice Smith")
        assert "Smith" == name2, f"Expected 'Smith', got '{name2}'"
        logger.info(f"✓ Honorific removal: 'Hon'ble Justice Smith' → '{name2}'")
        
        return True
    except Exception as e:
        logger.error(f"✗ Utility test failed: {e}")
        return False


def test_io_operations():
    """Test file I/O operations."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing I/O Operations")
    logger.info("=" * 60)
    
    try:
        from utils.io_utils import save_text, load_text, save_json, load_json
        
        # Test text file operations
        test_content = "<html><body>Test Cause List</body></html>"
        test_file = get_data_path('bronze') / 'test_file.html'
        
        save_text(test_content, test_file)
        logger.info(f"✓ Saved test file: {test_file}")
        
        loaded_content = load_text(test_file)
        assert loaded_content == test_content, "Content mismatch"
        logger.info(f"✓ Loaded test file: {len(loaded_content)} bytes")
        
        # Test JSON operations
        test_data = {'court': 'Test HC', 'cases': 150}
        json_file = get_data_path('bronze') / 'test_data.json'
        
        save_json(test_data, json_file)
        logger.info(f"✓ Saved JSON file: {json_file}")
        
        loaded_data = load_json(json_file)
        assert loaded_data == test_data, "Data mismatch"
        logger.info(f"✓ Loaded JSON file: {loaded_data}")
        
        # Cleanup
        test_file.unlink()
        json_file.unlink()
        logger.info("✓ Cleaned up test files")
        
        return True
    except Exception as e:
        logger.error(f"✗ I/O test failed: {e}")
        return False


def create_sample_data():
    """Create sample data for testing parsers."""
    logger.info("\n" + "=" * 60)
    logger.info("Creating Sample Data")
    logger.info("=" * 60)
    
    try:
        # Create a sample cause list HTML
        sample_html = """
        <html>
        <body>
        <h1>Daily Cause List - Test High Court</h1>
        <h2>Date: 15-11-2023</h2>
        <table>
            <tr>
                <th>S.No</th>
                <th>Case Number</th>
                <th>Parties</th>
                <th>Advocate</th>
                <th>Purpose</th>
            </tr>
            <tr>
                <td>1</td>
                <td>CRL.A/123/2023</td>
                <td>State vs Ram Kumar</td>
                <td>Adv. Sharma</td>
                <td>Arguments</td>
            </tr>
            <tr>
                <td>2</td>
                <td>CRL.A/124/2023</td>
                <td>State vs Shyam Verma</td>
                <td>Adv. Gupta</td>
                <td>Final Hearing</td>
            </tr>
            <tr>
                <td>3</td>
                <td>W.P/456/2023</td>
                <td>Priya Singh vs Union of India</td>
                <td>Adv. Mehta</td>
                <td>Notice</td>
            </tr>
        </table>
        </body>
        </html>
        """
        
        from utils.io_utils import save_with_metadata
        
        bronze_dir = get_data_path('bronze')
        sample_file = bronze_dir / 'cause_list_TEST_HC_20231115_sample.html'
        
        save_text(sample_html, sample_file)
        logger.info(f"✓ Created sample cause list: {sample_file}")
        
        # Save metadata
        metadata = {
            'court_code': 'TEST-HC',
            'list_date': '2023-11-15',
            'source_url': 'https://test.example.com/causelists',
            'fetch_timestamp': '2023-11-15T10:00:00'
        }
        
        metadata_file = sample_file.with_suffix('.json')
        save_with_metadata({'html_file': sample_file.name}, metadata_file, metadata['source_url'], metadata)
        logger.info(f"✓ Created metadata file: {metadata_file}")
        
        return str(sample_file)
        
    except Exception as e:
        logger.error(f"✗ Sample data creation failed: {e}")
        return None


def test_parser(sample_file: str):
    """Test the cause list parser."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Cause List Parser")
    logger.info("=" * 60)
    
    try:
        from parse.parse_cause_list import CauseListParser
        import pandas as pd
        
        parser = CauseListParser()
        output_file = parser.parse_and_save(sample_file)
        
        logger.info(f"✓ Parsed cause list to: {output_file}")
        
        # Load and verify parsed data
        df = pd.read_csv(output_file)
        logger.info(f"✓ Loaded DataFrame: {len(df)} rows, {len(df.columns)} columns")
        logger.info(f"  Columns: {', '.join(df.columns.tolist())}")
        
        # Check for expected case numbers
        if 'case_number' in df.columns:
            case_numbers = df['case_number'].tolist()
            logger.info(f"  Case numbers: {case_numbers}")
            
            expected_cases = ['CRL.A/123/2023', 'CRL.A/124/2023', 'W.P/456/2023']
            for expected in expected_cases:
                if any(expected in str(cn) for cn in case_numbers):
                    logger.info(f"  ✓ Found expected case: {expected}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Parser test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def test_database_operations():
    """Test database insert and query operations."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Database Operations")
    logger.info("=" * 60)
    
    try:
        from models.data_models import Court, Case, CaseType, CaseStatus
        from datetime import date
        
        db = DatabaseManager()
        
        # Use a unique timestamp-based code to avoid conflicts
        import time
        timestamp = int(time.time() * 1000) % 10000
        
        # Insert a test court
        test_court = Court(
            court_name="Test High Court",
            court_code=f"TEST-HC-{timestamp}",
            court_type="High Court",
            state="Test State"
        )
        
        court_id = db.insert_record(test_court)
        logger.info(f"✓ Inserted court with ID: {court_id}")
        
        # Query the court
        if court_id is None:
            raise ValueError("Failed to insert court")
        retrieved_court = db.query_by_id(Court, court_id)
        assert retrieved_court is not None, "Court not found"
        logger.info(f"✓ Retrieved court: {retrieved_court.court_name}")
        
        # Insert a test case
        test_case = Case(
            case_number="TEST/999/2023",
            normalized_case_number="TEST/999/2023",
            case_type=CaseType.CIVIL,
            case_status=CaseStatus.PENDING,
            filing_date=date.today(),
            court_id=court_id,
            petitioner="Test Petitioner",
            respondent="Test Respondent"
        )
        
        case_id = db.insert_record(test_case)
        logger.info(f"✓ Inserted case with ID: {case_id}")
        
        # Query cases
        cases = db.query_by_filter(Case, {'court_id': court_id})
        logger.info(f"✓ Found {len(cases)} cases for court {court_id}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Database operations test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def run_all_tests():
    """Run all tests in sequence."""
    logger.info("\n" + "🚀 " * 20)
    logger.info("JUSTICEGRAPH PHASE 1 - TEST SUITE")
    logger.info("🚀 " * 20 + "\n")
    
    tests = [
        ("Database Setup", test_database_setup),
        ("Data Models", test_data_models),
        ("Utilities", test_utilities),
        ("I/O Operations", test_io_operations),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            logger.error(f"✗ {test_name} raised exception: {e}")
            results[test_name] = False
    
    # Create sample data and test parser
    sample_file = create_sample_data()
    if sample_file:
        results["Sample Data Creation"] = True
        results["Parser"] = test_parser(sample_file)
    else:
        results["Sample Data Creation"] = False
        results["Parser"] = False
    
    # Test database operations
    results["Database Operations"] = test_database_operations()
    
    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        logger.info(f"{test_name:.<40} {status}")
    
    logger.info("=" * 60)
    logger.info(f"Tests Passed: {passed}/{total} ({passed/total*100:.1f}%)")
    logger.info("=" * 60 + "\n")
    
    if passed == total:
        logger.info("🎉 ALL TESTS PASSED! Phase 1 pipeline is ready.")
    else:
        logger.warning(f"⚠️  {total - passed} test(s) failed. Please review the logs.")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
