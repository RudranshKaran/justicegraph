"""
Quick Start Script for JusticeGraph Data Collection

This script demonstrates how to run the complete data collection pipeline.
Customize the parameters below and run: python run_collection.py
"""

import sys
from pathlib import Path
from datetime import datetime, date, timedelta

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from utils.logging_utils import get_logger
from utils.db_utils import DatabaseManager
from pipelines.phase1_pipeline import run_phase1_pipeline

logger = get_logger('run_collection')


def main():
    """
    Main execution function for data collection.
    """
    print("\n" + "="*60)
    print("  JUSTICEGRAPH - DATA COLLECTION")
    print("="*60 + "\n")
    
    # ========================================
    # CONFIGURATION - CUSTOMIZE THESE VALUES
    # ========================================
    
    # Court to scrape (options: 'DL-HC', 'BOM-HC', etc.)
    COURT_CODE = 'DL-HC'
    
    # Date range (format: YYYY-MM-DD)
    START_DATE = '2023-11-01'
    END_DATE = '2023-11-07'
    
    # Or use relative dates (e.g., last 7 days)
    # today = date.today()
    # START_DATE = (today - timedelta(days=7)).strftime('%Y-%m-%d')
    # END_DATE = today.strftime('%Y-%m-%d')
    
    print(f"📍 Target Court: {COURT_CODE}")
    print(f"📅 Date Range: {START_DATE} to {END_DATE}")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # ========================================
    # STEP 1: INITIALIZE DATABASE
    # ========================================
    
    print("🔧 Step 1: Initializing database...")
    try:
        db = DatabaseManager()
        db.create_tables()
        print("   ✓ Database initialized successfully\n")
    except Exception as e:
        print(f"   ✗ Database initialization failed: {e}")
        return
    
    # ========================================
    # STEP 2: RUN COMPLETE PIPELINE
    # ========================================
    
    print("🚀 Step 2: Running data collection pipeline...")
    print("   This will:")
    print("   - Scrape cause lists from court website")
    print("   - Parse HTML to structured data")
    print("   - Normalize and clean data")
    print("   - Validate and load to database")
    print()
    
    try:
        # Run the complete ETL pipeline
        run_phase1_pipeline(
            court_code=COURT_CODE,
            start_date=START_DATE,
            end_date=END_DATE
        )
        print("\n   ✓ Pipeline completed successfully!\n")
        
    except Exception as e:
        print(f"\n   ✗ Pipeline failed: {e}")
        logger.error(f"Pipeline execution error: {e}", exc_info=True)
        return
    
    # ========================================
    # STEP 3: VERIFY RESULTS
    # ========================================
    
    print("📊 Step 3: Verifying results...")
    try:
        from models.data_models import Court, Case, Hearing
        
        # Use get_table_count instead of query_all
        court_count = db.get_table_count(Court)
        case_count = db.get_table_count(Case)
        hearing_count = db.get_table_count(Hearing)
        
        print(f"   ✓ Courts in database: {court_count}")
        print(f"   ✓ Cases in database: {case_count}")
        print(f"   ✓ Hearings in database: {hearing_count}\n")
        
        # Show sample data if any exists
        if case_count > 0:
            cases = db.query_by_filter(Case, {}, limit=5)
            print("   Sample cases:")
            for case in cases:
                print(f"      - {case.case_number}: {case.petitioner_name} vs {case.respondent_name}")
        
    except Exception as e:
        print(f"   ⚠️  Could not verify results: {e}")
    
    # ========================================
    # SUMMARY
    # ========================================
    
    print("\n" + "="*60)
    print("  DATA COLLECTION COMPLETED")
    print("="*60)
    print(f"\n⏰ Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Data saved in: data/bronze/, data/silver/, data/gold/")
    print(f"📊 Database: SQLite at justicegraph.db")
    print(f"📝 Logs: logs/ directory\n")
    print("Next steps:")
    print("  1. Explore data: import pandas as pd; pd.read_csv('data/gold/...')")
    print("  2. Query database: python -c 'from utils.db_utils import DatabaseManager; ...'")
    print("  3. View logs: Get-Content logs\\*.log\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Collection interrupted by user. Exiting...")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        logger.error(f"Unexpected error in main: {e}", exc_info=True)
