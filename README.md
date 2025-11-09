# JusticeGraph - Intelligent Judicial Analytics Platform

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Phase](https://img.shields.io/badge/Phase-2%20Complete-success)](https://github.com/RudranshKaran/justicegraph)

JusticeGraph is a comprehensive data-driven platform designed to assist the Indian judicial system in reducing case backlogs, optimizing hearing schedules, and improving transparency through data science, machine learning, and intelligent optimization.

## 🎯 Project Vision

Transform judicial operations through:
- **Automated Data Collection** - Scrape and process judicial data from public sources
- **Intelligent Analytics** - Identify bottlenecks, trends, and performance metrics
- **AI-Powered Prioritization** - Rank cases by urgency using ML models
- **Optimized Scheduling** - Generate efficient hearing calendars with constraint programming
- **Predictive Insights** - Forecast case durations and resource needs

## 📊 Project Status

| Phase | Status | Description |
|-------|--------|-------------|
| **Phase 1** | ✅ Complete | Data collection, parsing, and ETL pipeline |
| **Phase 2** | ✅ Complete | EDA, ML models, prioritization, and scheduling optimization |
| **Phase 3** | 🔄 Planned | Web dashboard, real-time analytics, API development |

---

## 🚀 Quick Start

### For Phase 2 (Analytics & Optimization)

```bash
# Install dependencies
pip install -r requirements.txt

# Start exploring with Jupyter
jupyter notebook analysis/eda_overview.ipynb

# Or run quick analytics
python -c "from modeling.priority_model import calculate_priority_scores; df = calculate_priority_scores(); print(f'Prioritized {len(df)} cases')"
```

**📘 See [PHASE2_QUICKSTART.md](PHASE2_QUICKSTART.md) for detailed Phase 2 guide**

---

## 📁 Project Structure

```
JusticeGraph/
│
├── 📊 analysis/                # Phase 2: Exploratory Data Analysis
│   ├── case_duration_analysis.py    # Case duration metrics
│   ├── backlog_trends.py            # Backlog and disposal rates
│   ├── court_performance.py         # Court efficiency analysis
│   └── eda_overview.ipynb           # Interactive EDA notebook
│
├── 🤖 modeling/                # Phase 2: ML Models
│   ├── priority_model.py            # Case prioritization engine
│   ├── duration_prediction.py       # ML duration forecasting
│   └── model_utils.py               # Feature engineering utilities
│
├── ⚙️ optimization/            # Phase 2: Scheduling Engine
│   ├── scheduler.py                 # Intelligent hearing scheduler
│   ├── constraint_builder.py        # Scheduling constraints
│   └── optimization_utils.py        # Validation and metrics
│
├── 📈 visualization/           # Phase 2: Charts & Dashboards
│   ├── generate_visuals.py          # Plot generation
│   └── outputs/                     # Generated visualizations
│
├── 📄 reports/                 # Auto-generated reports
│   ├── EDA_SUMMARY.md
│   ├── PRIORITY_METRICS.md
│   ├── MODEL_METRICS.md
│   └── SCHEDULER_RESULTS.md
│
├── 💾 data/                    # Data storage (layered approach)
│   ├── bronze/                      # Raw scraped data
│   ├── silver/                      # Parsed structured data
│   └── gold/                        # Analysis-ready data
│       ├── prioritized_cases.csv
│       ├── optimized_schedule.csv
│       └── case_duration_analysis.csv
│
├── 🗄️ models/                  # Phase 1: Data Models
│   └── data_models.py               # SQLAlchemy ORM schemas
│
├── 🌐 ingest/                  # Phase 1: Web Scraping
│   ├── cause_list_ingest.py
│   ├── case_status_ingest.py
│   └── judgment_ingest.py
│
├── 🔧 parse/                   # Phase 1: Data Parsing
│   ├── parse_cause_list.py
│   └── parse_case_status.py
│
├── 🔄 pipelines/               # Workflow Orchestration
│   ├── phase1_pipeline.py           # Data collection pipeline
│   └── phase2_pipeline.py           # Analytics pipeline (TBD)
│
├── 🛠️ utils/                   # Shared Utilities
│   ├── db_utils.py                  # Database operations
│   ├── logging_utils.py             # Structured logging
│   └── io_utils.py                  # File I/O helpers
│
├── ⚙️ configs/                 # Configuration
│   ├── sources.yaml                 # Data source metadata
│   └── settings.env                 # Environment variables
│
├── 📚 documentation/           # Technical Documentation
│   ├── DATA_DICTIONARY.md
│   ├── PIPELINE_OVERVIEW.md
│   └── MODEL_DESIGN.md
│
├── requirements.txt            # Python dependencies
├── PHASE2_SUMMARY.md          # Phase 2 implementation details
├── PHASE2_QUICKSTART.md       # Phase 2 quick start guide
└── README.md                  # This file
```

4. **Configure environment**
   ```powershell
   # Copy example environment file
   cp configs/settings.env.example configs/settings.env
   
   # Edit settings.env with your database credentials
   ```

5. **Initialize database**
   ```python
   python -c "from utils.db_utils import DatabaseManager; db = DatabaseManager(); db.create_tables()"
   ```

### Configuration

Edit `configs/settings.env`:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/justicegraph

# Or use SQLite for development
# DATABASE_URL=sqlite:///justicegraph.db

# Logging
LOG_LEVEL=INFO

# Scraping Configuration
REQUEST_TIMEOUT=60
RATE_LIMIT_DELAY=2.0
```

## 📚 Usage Examples

### 1. Scrape Cause Lists

```python
from ingest.cause_list_ingest import CauseListScraper
from datetime import date

# Initialize scraper
scraper = CauseListScraper(
    court_code='DL-HC',
    base_url='https://delhihighcourt.nic.in'
)

# Fetch today's cause list
file_path = scraper.fetch_cause_list(date.today())
print(f"Saved to: {file_path}")
```

### 2. Parse Cause Lists

```python
from parse.parse_cause_list import CauseListParser

# Parse HTML to structured data
parser = CauseListParser()
output_path = parser.parse_and_save('data/bronze/cause_list_DL_HC_20231115.html')

# Load parsed data
import pandas as pd
df = pd.read_csv(output_path)
print(f"Parsed {len(df)} cases")
```

### 3. Normalize and Store Data

```python
from normalize.normalize_entities import normalize_case_data
from utils.db_utils import DatabaseManager

# Normalize data
normalized_df = normalize_case_data(df)

# Store in database
db = DatabaseManager()
# Insert logic here
```

### 4. Run Complete Pipeline

```python
from pipelines.phase1_pipeline import run_phase1_pipeline

# Execute full ETL workflow
run_phase1_pipeline(
    court_code='DL-HC',
    start_date='2023-11-01',
    end_date='2023-11-07'
)
```

## 🔧 Data Models

### Core Entities

- **Court**: Court metadata (name, code, location, jurisdiction)
- **Judge**: Judge information (name, designation, court assignment)
- **Case**: Legal case details (number, type, parties, status, dates)
- **Hearing**: Individual hearing records (date, judge, outcome)
- **CauseList**: Daily hearing schedules
- **Judgment**: Court orders and judgments

See `documentation/DATA_DICTIONARY.md` for complete field descriptions.

## 📊 Data Sources

### Currently Supported

- **eCourts Services Portal**: Case status and cause lists
- **High Court Websites**: Delhi HC, Bombay HC, etc. (customizable)
- **NJDG (National Judicial Data Grid)**: Aggregate statistics

### Planned

- **Supreme Court of India**: SCI case database
- **IndianKanoon**: Judgment repository
- **District Courts**: District-level data

See `documentation/SOURCE_REGISTRY.md` for detailed source information.

## 🧪 Testing

Run the test pipeline:

```powershell
python test_pipeline.py
```

Run unit tests:

```powershell
pytest tests/ -v --cov=.
```

## 📈 Pipeline Workflow

```
1. INGEST (Bronze Layer)
   ↓ Scrape HTML/PDF/JSON from sources
   ↓ Save with metadata and timestamps
   
2. PARSE (Silver Layer)
   ↓ Extract structured data from raw files
   ↓ Convert to DataFrames/CSV
   
3. NORMALIZE (Silver → Gold)
   ↓ Clean text (remove honorifics, standardize names)
   ↓ Normalize case numbers, dates, court names
   ↓ Resolve entity references
   
4. VALIDATE
   ↓ Check for nulls, duplicates, invalid formats
   ↓ Verify referential integrity
   
5. LOAD (Gold Layer → Database)
   ↓ Insert/upsert to PostgreSQL
   ↓ Update indexes and relationships
```

## 🛠️ Development

### Code Style

- Follow PEP 8
- Use type hints
- Document with docstrings
- Use `black` for formatting

```powershell
black .
flake8 .
mypy .
```

### Adding a New Data Source

1. Create scraper in `ingest/new_source_ingest.py`
2. Create parser in `parse/parse_new_source.py`
3. Add source metadata to `configs/sources.yaml`
4. Update documentation

## 📝 Logging

All operations are logged with structured JSON format:

```json
{
  "timestamp": "2023-11-15T14:30:22",
  "level": "INFO",
  "logger": "ingest",
  "message": "Scraper completed successfully",
  "scraper_name": "cause_list_ingest",
  "record_count": 150,
  "status": "success"
}
```

Logs are saved to `logs/` directory.

## 🔐 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `sqlite:///justicegraph.db` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `REQUEST_TIMEOUT` | HTTP request timeout (seconds) | `30` |
| `RATE_LIMIT_DELAY` | Delay between requests (seconds) | `2.0` |

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## ⚠️ Disclaimer

This project is for **research and educational purposes only**. Always respect the terms of service of data sources and comply with applicable laws regarding web scraping and data usage.

## 🎯 Roadmap

### Phase 1 (Current)
- ✅ Data collection infrastructure
- ✅ Parsing and normalization
- ✅ Database integration
- ✅ Data validation

### Phase 2 (Upcoming)
- AI-driven case prioritization
- Backlog prediction models
- Judge assignment optimization
- Interactive dashboards

### Phase 3 (Future)
- Real-time data updates
- Mobile application
- Public API
- Multi-language support

## 📞 Contact

For questions or collaborations:

- **GitHub**: [@RudranshKaran](https://github.com/RudranshKaran)
- **Project**: [justicegraph](https://github.com/RudranshKaran/justicegraph)

---

**Built with ❤️ to improve access to justice in India**
