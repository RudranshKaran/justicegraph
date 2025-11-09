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

## 🚀 Quick Start - MVP Dashboard

### Launch the Interactive Dashboard

```bash
# Install dependencies
pip install -r requirements_mvp.txt

# Generate sample data (if not already done)
python generate_sample_data.py

# Launch the dashboard
python run_mvp.py
```

**Dashboard will open at:** `http://localhost:8501`

**📘 See [docs/MVP_README.md](docs/MVP_README.md) for complete MVP guide**  
**📘 See [docs/QUICK_START.md](docs/QUICK_START.md) for quick reference**

---

## 📁 Project Structure

```
JusticeGraph/
│
├── 🎨 frontend/                # MVP Dashboard
│   └── app.py                       # Streamlit web interface
│
├── 📊 analysis/                # Exploratory Data Analysis
│   ├── case_duration_analysis.py    # Case duration metrics
│   ├── backlog_trends.py            # Backlog and disposal rates
│   ├── court_performance.py         # Court efficiency analysis
│   └── eda_overview.ipynb           # Interactive EDA notebook
│
├── 🤖 modeling/                # Machine Learning Models
│   ├── priority_model.py            # Case prioritization engine
│   ├── duration_prediction.py       # ML duration forecasting
│   └── model_utils.py               # Feature engineering utilities
│
├── ⚙️ optimization/            # Scheduling Engine
│   ├── scheduler.py                 # Intelligent hearing scheduler
│   ├── constraint_builder.py        # Scheduling constraints
│   └── optimization_utils.py        # Validation and metrics
│
├── 📈 visualization/           # Charts & Visualizations
│   └── generate_visuals.py          # Plot generation
│
├── 💾 data/                    # Data Storage (Layered)
│   ├── bronze/                      # Raw scraped data
│   ├── silver/                      # Parsed structured data
│   └── gold/                        # Analysis-ready data
│       ├── prioritized_cases.csv
│       ├── optimized_schedule.csv
│       ├── case_duration_analysis.csv
│       └── backlog_trends.csv
│
├── 🗄️ models/                  # Data Models
│   └── data_models.py               # SQLAlchemy ORM schemas
│
├── 🌐 ingest/                  # Web Scraping
│   ├── cause_list_ingest.py
│   ├── case_status_ingest.py
│   └── judgment_ingest.py
│
├── 🔧 parse/                   # Data Parsing
│   └── parse_cause_list.py
│
├── 🔄 normalize/               # Data Cleaning
│   └── clean_text_utils.py
│
├── 🔄 pipelines/               # Workflow Orchestration
│   └── phase1_pipeline.py           # Data collection pipeline
│
├── 🛠️ utils/                   # Shared Utilities
│   ├── db_utils.py                  # Database operations
│   ├── http_utils.py                # HTTP utilities
│   ├── logging_utils.py             # Structured logging
│   └── io_utils.py                  # File I/O helpers
│
├── ⚙️ configs/                 # Configuration
│   ├── sources.yaml                 # Data source metadata
│   └── settings.env                 # Environment variables
│
├── 📚 docs/                    # Documentation
│   ├── MVP_README.md                # MVP setup guide
│   ├── QUICK_START.md               # Quick reference
│   ├── DATA_DICTIONARY.md           # Data schema
│   ├── PIPELINE_OVERVIEW.md         # Pipeline architecture
│   ├── PHASE2_SUMMARY.md            # Phase 2 details
│   └── ISSUES_RESOLVED.md           # Bug fixes and resolutions
│
├── generate_sample_data.py    # Sample data generator
├── run_mvp.py                 # MVP launcher
├── setup_mvp.py               # Automated setup
├── test_mvp.py                # Test suite
├── validate_mvp.py            # Validation script
├── requirements_mvp.txt       # Dependencies
└── README.md                  # This file
```

## 📊 Data Sources

### Currently Supported

- **eCourts Services Portal**: Case status and cause lists
- **High Court Websites**: Delhi HC, Bombay HC, etc. (customizable)
- **NJDG (National Judicial Data Grid)**: Aggregate statistics

### Planned

- **Supreme Court of India**: SCI case database
- **IndianKanoon**: Judgment repository
- **District Courts**: District-level data

## 📈 MVP Features

### Analytics Dashboard 📊
- **Case Volume Trends**: Track daily case filing and disposal rates
- **Backlog Analysis**: Visualize pending cases by court and case type
- **Court Performance**: Compare efficiency metrics across jurisdictions
- **Duration Analysis**: Analyze average case resolution times

### Case Prioritization 🎯
- **Smart Scoring**: ML-driven priority calculation based on:
  - Case age and urgency
  - Case type and complexity
  - Historical hearing patterns
- **Filter & Export**: Search by priority, court, or case type
- **CSV Download**: Export prioritized cases for further analysis

### Optimized Scheduling 📅
- **Intelligent Allocation**: OR-Tools based constraint optimization
- **Judge Workload Balancing**: Ensure equitable case distribution
- **Timeline Visualization**: Gantt chart of scheduled hearings
- **Schedule Export**: Download hearing calendars

## 🧪 Testing

Run the MVP test suite:

```powershell
python test_mvp.py
```

Validate MVP setup:

```powershell
python validate_mvp.py
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

### Phase 1 - Data Infrastructure ✅
- ✅ Data collection and scraping framework
- ✅ Parsing and normalization pipeline
- ✅ Database integration (SQLAlchemy ORM)
- ✅ Data validation and quality checks

### Phase 2 - Analytics & Intelligence ✅
- ✅ Exploratory Data Analysis (EDA)
- ✅ AI-driven case prioritization engine
- ✅ ML-based duration prediction models
- ✅ Intelligent hearing scheduler (OR-Tools)
- ✅ Interactive Streamlit dashboard
- ✅ Data visualizations (Plotly)

### Phase 3 - Production Deployment 🔄
- 🔄 Real-time data updates
- 🔄 REST API development
- 🔄 User authentication and roles
- 🔄 Mobile-responsive interface
- 🔄 Cloud deployment (AWS/Azure)

### Phase 4 - Advanced Features 📋
- 📋 Natural Language Processing for judgments
- 📋 Predictive analytics for case outcomes
- 📋 Multi-language support (Hindi, regional languages)
- 📋 Integration with eCourts portal
- 📋 Public API for researchers

## 📞 Contact

For questions or collaborations:

- **GitHub**: [@RudranshKaran](https://github.com/RudranshKaran)
- **Project**: [justicegraph](https://github.com/RudranshKaran/justicegraph)

---

**Built with ❤️ to improve access to justice in India**
