# JusticeGraph Data Collection - Execution Guide

## 📖 Overview

This guide explains **how data collection works** in JusticeGraph and **how to execute it** step-by-step.

---

## 🎯 Data Collection Process

### Phase 1 Pipeline Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   INGEST     │ --> │    PARSE     │ --> │  NORMALIZE   │ --> │   VALIDATE   │
│   (Bronze)   │     │   (Silver)   │     │   (Gold)     │     │  & LOAD DB   │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
  Raw HTML/PDF       Structured CSV      Clean & Standard      PostgreSQL
```

### The 4-Stage ETL Process

#### **Stage 1: INGEST (Web Scraping)**
- **What happens**: Fetches raw data from court websites
- **Input**: Court URLs, date ranges, search parameters
- **Process**: HTTP requests with retry logic and rate limiting
- **Output**: Raw HTML/PDF files saved to `data/bronze/`
- **Example**: `cause_list_DL_HC_20231115.html`

#### **Stage 2: PARSE (Data Extraction)**
- **What happens**: Extracts structured data from raw files
- **Input**: Raw files from bronze layer
- **Process**: BeautifulSoup/regex parsing to extract tables and fields
- **Output**: CSV/JSON files saved to `data/silver/`
- **Example**: `cause_list_DL_HC_20231115_parsed.csv`

#### **Stage 3: NORMALIZE (Data Cleaning)**
- **What happens**: Cleans and standardizes data
- **Input**: Parsed CSV files from silver layer
- **Process**: 
  - Normalize case numbers: `"CRL. A. 123 of 2023"` → `"CRL.A/123/2023"`
  - Clean names: `"Hon'ble Mr. Justice JOHN DOE"` → `"John Doe"`
  - Standardize dates, court names, etc.
- **Output**: Clean CSV files ready for database

#### **Stage 4: VALIDATE & LOAD**
- **What happens**: Quality checks and database insertion
- **Input**: Normalized data
- **Process**: Check for duplicates, nulls, invalid formats, then insert to DB
- **Output**: Data stored in PostgreSQL/SQLite database

---

## 🚀 Execution Methods

### Method 1: Run Complete Pipeline (Recommended)

**Use case**: Automated end-to-end data collection for a date range

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run full pipeline for a specific court and date range
python -c "from pipelines.phase1_pipeline import run_phase1_pipeline; run_phase1_pipeline('DL-HC', '2023-11-01', '2023-11-07')"
```

**What this does**:
1. Scrapes cause lists for Delhi High Court from Nov 1-7, 2023
2. Parses all downloaded files
3. Normalizes the data
4. Validates and loads into database
5. Logs all operations

---

### Method 2: Step-by-Step Execution

**Use case**: When you want to run individual stages for testing or debugging

#### **Step 1: Scrape Data (INGEST)**

```python
from ingest.cause_list_ingest import CauseListScraper
from datetime import date

# Initialize scraper for Delhi High Court
scraper = CauseListScraper(
    court_code='DL-HC',
    base_url='https://delhihighcourt.nic.in'
)

# Fetch today's cause list
file_path = scraper.fetch_cause_list(date.today())
print(f"✓ Saved to: {file_path}")

# Or fetch for a date range
from datetime import timedelta
start_date = date(2023, 11, 1)
for i in range(7):  # 7 days
    current_date = start_date + timedelta(days=i)
    file_path = scraper.fetch_cause_list(current_date)
    print(f"✓ Fetched {current_date}: {file_path}")
```

#### **Step 2: Parse Data (PARSE)**

```python
from parse.parse_cause_list import CauseListParser
import pandas as pd

# Initialize parser
parser = CauseListParser()

# Parse a single file
input_file = 'data/bronze/cause_list_DL_HC_20231115.html'
output_path = parser.parse_and_save(input_file)
print(f"✓ Parsed to: {output_path}")

# Load and inspect the parsed data
df = pd.read_csv(output_path)
print(f"✓ Extracted {len(df)} cases")
print(f"  Columns: {list(df.columns)}")
print(df.head())
```

#### **Step 3: Normalize Data (NORMALIZE)**

```python
from normalize.clean_text_utils import normalize_case_number, clean_name
import pandas as pd

# Load parsed data
df = pd.read_csv('data/silver/cause_list_DL_HC_20231115_parsed.csv')

# Normalize case numbers
df['case_number'] = df['case_number'].apply(
    lambda x: normalize_case_number(str(x)) if pd.notna(x) else x
)

# Clean names
df['petitioner'] = df['petitioner'].apply(
    lambda x: clean_name(str(x)) if pd.notna(x) else x
)

# Save normalized data
df.to_csv('data/gold/cause_list_DL_HC_20231115_normalized.csv', index=False)
print(f"✓ Normalized {len(df)} records")
```

#### **Step 4: Load to Database (LOAD)**

```python
from utils.db_utils import DatabaseManager
from models.data_models import Court, Case, Hearing
import pandas as pd

# Initialize database
db = DatabaseManager()
db.create_tables()

# Load normalized data
df = pd.read_csv('data/gold/cause_list_DL_HC_20231115_normalized.csv')

# Insert court if not exists
court_data = {
    'court_name': 'Delhi High Court',
    'court_code': 'DL-HC',
    'court_type': 'High Court',
    'state': 'Delhi'
}
court_id = db.insert(Court(**court_data))
print(f"✓ Court ID: {court_id}")

# Insert cases
for _, row in df.iterrows():
    case_data = {
        'case_number': row['case_number'],
        'case_type': 'criminal' if 'CRL' in row['case_number'] else 'civil',
        'filing_date': row['list_date'],
        'petitioner_name': row['petitioner'],
        'respondent_name': row['respondent'],
        'court_id': court_id
    }
    case_id = db.insert(Case(**case_data))

print(f"✓ Inserted {len(df)} cases")
```

---

## 🎮 Interactive Python Session

**Use case**: Exploratory data collection and testing

```powershell
# Start Python interactive shell
python

# In Python shell:
>>> from ingest.cause_list_ingest import CauseListScraper
>>> from datetime import date
>>> 
>>> # Quick scrape
>>> scraper = CauseListScraper('DL-HC', 'https://delhihighcourt.nic.in')
>>> file_path = scraper.fetch_cause_list(date(2023, 11, 15))
>>> print(file_path)
>>> 
>>> # Quick parse
>>> from parse.parse_cause_list import CauseListParser
>>> parser = CauseListParser()
>>> output = parser.parse_and_save(file_path)
>>> 
>>> # Quick view
>>> import pandas as pd
>>> df = pd.read_csv(output)
>>> print(df.head())
```

---

## 📋 Pre-Execution Checklist

Before running data collection, ensure:

- [x] **Virtual environment activated**: `.\venv\Scripts\Activate.ps1`
- [x] **Dependencies installed**: `pip install -r requirements.txt`
- [x] **Configuration set**: Edit `configs/settings.env` with correct values
- [x] **Database initialized**: Run `python -c "from utils.db_utils import DatabaseManager; db = DatabaseManager(); db.create_tables()"`
- [x] **Data directories exist**: `data/bronze/`, `data/silver/`, `data/gold/`
- [x] **Internet connection**: Required for web scraping
- [x] **Court URL accessible**: Check if target court website is online

---

## ⚙️ Configuration

### Edit `configs/settings.env`

```env
# Database (SQLite for testing, PostgreSQL for production)
DATABASE_URL=sqlite:///justicegraph.db

# Logging
LOG_LEVEL=INFO
LOG_TO_FILE=true
JSON_LOGS=false

# Scraping (important for avoiding IP blocks!)
REQUEST_TIMEOUT=60
RETRY_ATTEMPTS=3
RATE_LIMIT_DELAY=2.0  # Wait 2 seconds between requests
VERIFY_SSL=true
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64)...

# Data directories
DATA_DIR=data
BRONZE_DIR=data/bronze
SILVER_DIR=data/silver
GOLD_DIR=data/gold
```

### Modify `configs/sources.yaml` for Different Courts

```yaml
courts:
  - code: DL-HC
    name: Delhi High Court
    url: https://delhihighcourt.nic.in
    cause_list_endpoint: /causelists
    encoding: utf-8
    
  - code: BOM-HC
    name: Bombay High Court
    url: https://bombayhighcourt.nic.in
    cause_list_endpoint: /causelists
    encoding: utf-8
```

---

## 🔍 Monitoring & Logs

All operations are logged to:
- **Console**: Real-time progress
- **Log file**: `logs/justicegraph_YYYYMMDD.log`

### View Logs

```powershell
# Tail logs in real-time
Get-Content logs\justicegraph_20231115.log -Wait -Tail 50

# Search for errors
Select-String -Path logs\*.log -Pattern "ERROR"

# Count scraped records
Select-String -Path logs\*.log -Pattern "Scraped \d+ records"
```

---

## 📊 Verify Data Collection

### Check Files

```powershell
# Count files in each layer
(Get-ChildItem data\bronze\*.html).Count
(Get-ChildItem data\silver\*.csv).Count
(Get-ChildItem data\gold\*.csv).Count
```

### Check Database

```python
from utils.db_utils import DatabaseManager
from models.data_models import Court, Case, Hearing

db = DatabaseManager()

# Count records
courts = db.query_all(Court)
cases = db.query_all(Case)
hearings = db.query_all(Hearing)

print(f"Courts: {len(courts)}")
print(f"Cases: {len(cases)}")
print(f"Hearings: {len(hearings)}")
```

---

## 🚨 Troubleshooting

### Issue: "Connection timeout"
**Solution**: Increase `REQUEST_TIMEOUT` in `settings.env` to 120

### Issue: "Too many requests / IP blocked"
**Solution**: Increase `RATE_LIMIT_DELAY` to 5.0 seconds

### Issue: "No data extracted"
**Solution**: Court website structure may have changed. Check HTML in `data/bronze/` and update parser regex patterns

### Issue: "Database error"
**Solution**: Run `db.create_tables()` to ensure schema exists

### Issue: "Import errors"
**Solution**: Ensure you're in project root and virtual environment is activated

---

## 🎯 Quick Start Commands

```powershell
# 1. Activate environment
.\venv\Scripts\Activate.ps1

# 2. Initialize database
python -c "from utils.db_utils import DatabaseManager; db = DatabaseManager(); db.create_tables()"

# 3. Run test to verify everything works
python test_pipeline.py

# 4. Scrape data for one day (customize date and court)
python -c "from ingest.cause_list_ingest import CauseListScraper; from datetime import date; scraper = CauseListScraper('DL-HC', 'https://delhihighcourt.nic.in'); print(scraper.fetch_cause_list(date(2023, 11, 15)))"

# 5. Run complete pipeline (change dates as needed)
python -c "from pipelines.phase1_pipeline import run_phase1_pipeline; run_phase1_pipeline('DL-HC', '2023-11-01', '2023-11-07')"
```

---

## 📈 Next Steps

After successful data collection:

1. **Explore Data**: Use Jupyter notebooks to analyze collected data
2. **Visualize**: Create dashboards with Plotly/Dash
3. **Export**: Generate reports in CSV/Excel format
4. **Scale**: Add more courts and data sources
5. **Automate**: Schedule daily runs using Windows Task Scheduler or cron

---

## 🔗 Related Documentation

- **Pipeline Architecture**: `documentation/PIPELINE_OVERVIEW.md`
- **Data Dictionary**: `documentation/DATA_DICTIONARY.md`
- **Source Registry**: `documentation/SOURCE_REGISTRY.md`
- **API Reference**: Code docstrings in each module

---

## ⚠️ Important Notes

1. **Rate Limiting**: Always respect court website rate limits (2-5 second delays)
2. **Terms of Service**: Review each court's ToS before scraping
3. **Data Privacy**: Handle judicial data responsibly and ethically
4. **Testing**: Start with small date ranges (1-2 days) before scaling
5. **Backups**: Regularly backup both files and database

---

**Questions?** Check the [README.md](../README.md) or raise an issue on GitHub.

**Happy Data Collecting! 📊⚖️**
