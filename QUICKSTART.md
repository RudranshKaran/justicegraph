# JusticeGraph Quick Start Guide

## 🚀 Installation (5 minutes)

### 1. Clone or navigate to project
```powershell
cd c:\Users\rudra\Desktop\projects\justicegraph
```

### 2. Create virtual environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies
```powershell
pip install -r requirements.txt
```

### 4. Configure environment
```powershell
# Copy example config
copy configs\settings.env.example configs\settings.env

# Edit settings.env with your database URL
# For development, you can use SQLite (default)
# DATABASE_URL=sqlite:///justicegraph.db
```

### 5. Run setup
```powershell
python setup.py
```

---

## 📝 Common Commands

### Initialize Database
```python
from utils.db_utils import DatabaseManager
db = DatabaseManager()
db.create_tables()
```

### Run Tests
```powershell
python test_pipeline.py
```

### Scrape Cause Lists
```python
from ingest.cause_list_ingest import CauseListScraper
from datetime import date

scraper = CauseListScraper('DL-HC', 'https://delhihighcourt.nic.in')
file_path = scraper.fetch_cause_list(date.today())
```

### Parse Cause Lists
```python
from parse.parse_cause_list import CauseListParser

parser = CauseListParser()
output = parser.parse_and_save('data/bronze/cause_list_file.html')
```

### Run Complete Pipeline
```python
from pipelines.phase1_pipeline import run_phase1_pipeline

run_phase1_pipeline('DL-HC', '2023-11-01', '2023-11-07')
```

### Or via command line
```powershell
python pipelines\phase1_pipeline.py DL-HC 2023-11-01 2023-11-07
```

---

## 📊 Project Structure Quick Reference

```
justicegraph/
│
├── data/                   # Data storage
│   ├── bronze/            # Raw scraped data
│   ├── silver/            # Parsed structured data
│   └── gold/              # Normalized analysis-ready data
│
├── models/                 # Database models
│   └── data_models.py     # SQLAlchemy ORM models
│
├── ingest/                 # Data collection
│   ├── cause_list_ingest.py
│   ├── case_status_ingest.py
│   └── judgment_ingest.py
│
├── parse/                  # Data parsing
│   ├── parse_cause_list.py
│   ├── parse_case_status.py
│   └── parse_judgment.py
│
├── normalize/              # Data normalization
│   ├── normalize_entities.py
│   └── clean_text_utils.py
│
├── pipelines/              # Workflow orchestration
│   └── phase1_pipeline.py
│
├── validation/             # Data quality
│   └── data_validation.py
│
├── utils/                  # Utilities
│   ├── http_utils.py
│   ├── io_utils.py
│   ├── logging_utils.py
│   └── db_utils.py
│
├── configs/                # Configuration
│   ├── sources.yaml
│   └── settings.env
│
└── documentation/          # Docs
    ├── DATA_DICTIONARY.md
    ├── SOURCE_REGISTRY.md
    └── PIPELINE_OVERVIEW.md
```

---

## 🔧 Configuration Files

### `configs/settings.env`
```env
DATABASE_URL=sqlite:///justicegraph.db  # or PostgreSQL
LOG_LEVEL=INFO
REQUEST_TIMEOUT=60
RATE_LIMIT_DELAY=2.0
```

### `configs/sources.yaml`
Defines data sources, URLs, and update frequencies

---

## 🎯 Example Workflows

### Workflow 1: Daily Cause List Collection

```python
from ingest.cause_list_ingest import CauseListScraper
from parse.parse_cause_list import CauseListParser
from datetime import date

# 1. Scrape
scraper = CauseListScraper('DL-HC', 'https://delhihighcourt.nic.in')
html_file = scraper.fetch_cause_list(date.today())

# 2. Parse
parser = CauseListParser()
csv_file = parser.parse_and_save(html_file)

# 3. Load parsed data
import pandas as pd
df = pd.read_csv(csv_file)
print(f"Found {len(df)} cases")
```

### Workflow 2: Case Status Collection

```python
from ingest.case_status_ingest import CaseStatusScraper

scraper = CaseStatusScraper('DL-HC', 'https://delhihighcourt.nic.in')

# Fetch single case
case_data = scraper.fetch_case_status('CRL.A/123/2023')

# Fetch multiple cases
case_numbers = ['CRL.A/123/2023', 'CRL.A/124/2023']
results = scraper.fetch_multiple_cases(case_numbers)
```

### Workflow 3: Complete ETL Pipeline

```python
from pipelines.phase1_pipeline import phase1_pipeline
from datetime import date

result = phase1_pipeline(
    court_code='DL-HC',
    base_url='https://delhihighcourt.nic.in',
    start_date=date(2023, 11, 1),
    end_date=date(2023, 11, 7)
)

print(result)
# {
#   'status': 'completed',
#   'files_ingested': 7,
#   'records_loaded': 1050,
#   'duration_seconds': 45.2
# }
```

---

## 🐛 Troubleshooting

### Import Errors
```powershell
# Make sure you're in the project root
cd c:\Users\rudra\Desktop\projects\justicegraph

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

### Database Connection Errors
```python
# Check your DATABASE_URL in configs/settings.env
# For development, use SQLite:
DATABASE_URL=sqlite:///justicegraph.db

# For production PostgreSQL:
DATABASE_URL=postgresql://user:password@localhost:5432/justicegraph
```

### Scraping Errors
- Check internet connection
- Verify court website URLs in `configs/sources.yaml`
- Increase `REQUEST_TIMEOUT` in settings.env
- Check logs in `logs/` directory

---

## 📚 Documentation

- **README.md**: Project overview and setup
- **DATA_DICTIONARY.md**: Complete data schema
- **PIPELINE_OVERVIEW.md**: ETL architecture details
- **SOURCE_REGISTRY.md**: Data source information

---

## 🆘 Getting Help

### Check Logs
```powershell
# View recent logs
cat logs\ingest.log
cat logs\pipeline.log
```

### Run Tests
```powershell
python test_pipeline.py
```

### Validate Data
```python
from validation.data_validation import run_validation_checks

run_validation_checks('data/gold/cause_list_parsed.csv')
```

---

## 🎓 Learning Path

1. **Start Here**: README.md
2. **Understand Data**: DATA_DICTIONARY.md
3. **Learn Pipeline**: PIPELINE_OVERVIEW.md
4. **Run Tests**: `python test_pipeline.py`
5. **Try Examples**: See "Example Workflows" above
6. **Customize**: Add your own data sources

---

## 📞 Support

- **GitHub**: https://github.com/RudranshKaran/justicegraph
- **Issues**: Report bugs and feature requests
- **Discussions**: Ask questions and share ideas

---

**Happy Coding! 🚀**

*JusticeGraph Team*
