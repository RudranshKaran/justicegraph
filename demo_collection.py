"""
Simple Demo: Individual Stage Execution

This script shows how to run each stage of the pipeline separately.
Good for learning and debugging.
"""

import sys
from pathlib import Path
from datetime import date

sys.path.append(str(Path(__file__).parent))

print("\n" + "="*70)
print("  JUSTICEGRAPH - STEP-BY-STEP DEMO")
print("="*70 + "\n")

# ============================================================================
# STAGE 1: SCRAPE (INGEST)
# ============================================================================

print("📥 STAGE 1: SCRAPING DATA (INGEST)")
print("-" * 70)

from ingest.cause_list_ingest import CauseListScraper

print("Initializing scraper for Delhi High Court...")
scraper = CauseListScraper(
    court_code='TEST_HC',  # Using test code
    base_url='https://delhihighcourt.nic.in'
)

# For demo purposes, we'll create a sample file instead of real scraping
# In production, you would use: scraper.fetch_cause_list(date(2023, 11, 15))

print("✓ Scraper initialized")
print(f"  Court Code: TEST_HC")
print(f"  Bronze Directory: {scraper.bronze_dir}\n")

# ============================================================================
# STAGE 2: PARSE (EXTRACT)
# ============================================================================

print("📝 STAGE 2: PARSING DATA (EXTRACT)")
print("-" * 70)

from parse.parse_cause_list import CauseListParser
import pandas as pd

print("Initializing parser...")
parser = CauseListParser()

# Check if we have sample data from test_pipeline
sample_file = Path('data/bronze/cause_list_TEST_HC_20231115_sample.html')

if sample_file.exists():
    print(f"Found sample file: {sample_file}")
    
    # Parse the file
    output_path = parser.parse_and_save(str(sample_file))
    print(f"✓ Parsed successfully")
    print(f"  Output: {output_path}")
    
    # Load and display
    df = pd.read_csv(output_path)
    print(f"\n📊 Parsed Data Preview:")
    print(f"  Total rows: {len(df)}")
    print(f"  Columns: {', '.join(df.columns[:6])}...\n")
    print(df[['case_number', 'case_title', 'petitioner', 'respondent']].head())
    print()
else:
    print("ℹ️  No sample file found. Run test_pipeline.py first to create sample data.")
    print("  Command: python test_pipeline.py\n")

# ============================================================================
# STAGE 3: NORMALIZE (CLEAN)
# ============================================================================

print("\n🧹 STAGE 3: NORMALIZING DATA (CLEAN)")
print("-" * 70)

from normalize.clean_text_utils import (
    normalize_case_number,
    clean_name,
    remove_honorifics
)

print("Testing normalization functions:\n")

# Test case number normalization
test_cases = [
    "CRL. A. 123 of 2023",
    "W.P. 456/2023",
    "CIVIL APPEAL NO. 789 of 2022"
]

print("Case Number Normalization:")
for case in test_cases:
    normalized = normalize_case_number(case)
    print(f"  '{case}' → '{normalized}'")

print()

# Test name cleaning
test_names = [
    "Hon'ble Mr. Justice RAJESH KUMAR",
    "  JOHN DOE vs. JANE DOE  ",
    "Mrs. ANITA SHARMA"
]

print("Name Cleaning:")
for name in test_names:
    cleaned = clean_name(name)
    print(f"  '{name}' → '{cleaned}'")

print()

# Test honorific removal
test_honorifics = [
    "Hon'ble Justice P.K. Sharma",
    "Mr. John Smith",
    "Dr. Rajesh Kumar"
]

print("Honorific Removal:")
for name in test_honorifics:
    cleaned = remove_honorifics(name)
    print(f"  '{name}' → '{cleaned}'")

print()

# ============================================================================
# STAGE 4: DATABASE OPERATIONS
# ============================================================================

print("\n💾 STAGE 4: DATABASE OPERATIONS")
print("-" * 70)

from utils.db_utils import DatabaseManager
from models.data_models import Court, Case, Judge

print("Initializing database...")
db = DatabaseManager()
db.create_tables()
print("✓ Database tables created/verified\n")

print("Database Statistics:")
try:
    from models.data_models import Hearing
    
    # Use get_table_count instead of query_all
    court_count = db.get_table_count(Court)
    case_count = db.get_table_count(Case)
    judge_count = db.get_table_count(Judge)
    hearing_count = db.get_table_count(Hearing)
    
    print(f"  Courts: {court_count}")
    print(f"  Cases: {case_count}")
    print(f"  Judges: {judge_count}")
    print(f"  Hearings: {hearing_count}")
    
    # Query sample data if any exists
    if court_count > 0:
        courts = db.query_by_filter(Court, {}, limit=3)
        print(f"\n  Sample Courts:")
        for court in courts:
            print(f"    - [{court.court_code}] {court.court_name}")
    
    if case_count > 0:
        cases = db.query_by_filter(Case, {}, limit=3)
        print(f"\n  Sample Cases:")
        for case in cases:
            print(f"    - {case.case_number}: {case.case_type}")
    
except Exception as e:
    print(f"  ⚠️  Error querying database: {e}")

print()

# ============================================================================
# FILE SYSTEM CHECK
# ============================================================================

print("\n📁 FILE SYSTEM CHECK")
print("-" * 70)

data_dir = Path('data')

for layer in ['bronze', 'silver', 'gold']:
    layer_path = data_dir / layer
    if layer_path.exists():
        files = list(layer_path.glob('*'))
        non_gitkeep = [f for f in files if f.name != '.gitkeep']
        print(f"  {layer.upper():7} layer: {len(non_gitkeep)} files")
        
        if non_gitkeep:
            for f in non_gitkeep[:3]:
                size_kb = f.stat().st_size / 1024
                print(f"    - {f.name} ({size_kb:.1f} KB)")
    else:
        print(f"  {layer.upper():7} layer: Directory not found")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*70)
print("  DEMO COMPLETED")
print("="*70)
print("""
Key Takeaways:
  1. INGEST: Use CauseListScraper to fetch raw HTML from court websites
  2. PARSE: Use CauseListParser to extract structured data to CSV
  3. NORMALIZE: Use clean_text_utils to standardize names, case numbers, etc.
  4. LOAD: Use DatabaseManager to store data in SQLite/PostgreSQL

Next Steps:
  • Run full pipeline: python run_collection.py
  • Run tests: python test_pipeline.py
  • Read docs: EXECUTION_GUIDE.md

For production use:
  1. Configure real court URLs in configs/sources.yaml
  2. Set up proper database in configs/settings.env
  3. Adjust rate limits and timeouts for your use case
  4. Schedule automated runs with Task Scheduler/cron
""")
