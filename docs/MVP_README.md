# JusticeGraph - MVP Version

## 🎯 Overview

**JusticeGraph MVP** is a lightweight demonstration of an intelligent judicial analytics and optimization platform. This version showcases:

- **Automated Judicial Analytics** - Case duration analysis, backlog trends, court performance metrics
- **ML-Based Case Prioritization** - Multi-factor weighted scoring system for urgent case identification
- **Optimized Hearing Scheduling** - AI-generated hearing calendars with constraint programming
- **Interactive Web Dashboard** - Clean Streamlit interface for data exploration

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- 5-10 minutes for setup

### Installation

1. **Navigate to project directory**
   ```powershell
   cd C:\Users\rudra\Desktop\projects\justicegraph
   ```

2. **Install MVP dependencies**
   ```powershell
   pip install -r requirements_mvp.txt
   ```
   
   **Core packages installed:**
   - `streamlit` - Web dashboard framework
   - `plotly` - Interactive visualizations
   - `pandas` - Data manipulation
   - `numpy` - Numerical computing
   - `scikit-learn` - Machine learning

3. **Generate sample data** (if not already present)
   ```powershell
   python generate_sample_data.py
   ```
   
   This creates 4 CSV files in `data/gold/`:
   - `prioritized_cases.csv` - 150 cases with ML priority scores
   - `optimized_schedule.csv` - 20-day hearing calendar
   - `case_duration_analysis.csv` - Duration metrics by case type
   - `backlog_trends.csv` - Court-wise backlog statistics

4. **Launch the MVP dashboard**
   ```powershell
   python run_mvp.py
   ```
   
   Or directly:
   ```powershell
   streamlit run frontend/app.py
   ```

5. **Open in browser**
   - URL: `http://localhost:8501`
   - Dashboard will auto-open in your default browser

---

## 📊 MVP Features

### 1. Analytics Dashboard 📈

**Key Metrics Display:**
- Total cases analyzed
- Average priority score
- High priority case count
- Average case age

**Visualizations:**
- **Case Type Distribution** (Pie Chart) - Breakdown of criminal, civil, writ, appeal cases
- **Priority Score Distribution** (Histogram) - Distribution of ML-generated scores
- **Case Load by Court** (Bar Chart) - Comparative court workload
- **Case Age Distribution** (Box Plot) - Age patterns by case type
- **Duration Analysis Table** - Statistical summary by case type

**Use Case:** Executive overview for judicial administrators to understand system-wide patterns.

---

### 2. Case Prioritization 🎯

**Features:**
- **ML Priority Scoring** - Multi-factor weighted algorithm:
  - Case age (30%) - Older cases get higher priority
  - Case type (25%) - Criminal > Writ > Appeal > Civil
  - Hearing count (20%) - More adjournments = higher priority
  - Court workload (15%) - Backlog severity factor
  - Urgency factors (10%) - Special circumstances

- **Interactive Filters:**
  - Filter by court (Delhi HC, Mumbai HC, etc.)
  - Filter by case type (Criminal, Civil, Writ, etc.)
  - Filter by priority category (High/Medium/Low)

- **Sortable Data Table** - Top 50 prioritized cases with:
  - Case number
  - Court code
  - Case type
  - Priority score (0-100)
  - Age in days
  - Hearing count
  - Priority category

- **CSV Export** - Download filtered results for reporting

**Use Case:** Case managers can identify urgent cases requiring immediate attention and allocate resources efficiently.

---

### 3. Optimized Schedule 📅

**Schedule Metrics:**
- Total cases scheduled
- Judges involved
- Hearing days covered
- Average priority of scheduled cases

**Visualizations:**
- **Scheduled Hearings Timeline** (Line Chart) - Daily hearing distribution per judge
- **Judge Workload Distribution** (Bar Chart) - Equitable workload analysis

**Schedule Table:**
- Hearing date
- Case number
- Assigned judge
- Priority score
- Estimated duration

**Export Options:**
- Download complete schedule as CSV
- Import into calendar systems

**Use Case:** Court administrators can optimize resource utilization, ensure high-priority cases are scheduled first, and balance judge workloads.

---

## 🏗️ Technical Architecture

### Frontend (Streamlit)
- **Framework:** Streamlit 1.28+
- **Layout:** Wide mode with 3-tab interface
- **Charts:** Plotly for interactive visualizations
- **Data Loading:** Direct CSV file reading with caching
- **Responsive:** Works on desktop browsers

### Data Pipeline
```
Raw Court Data (Bronze Layer)
         ↓
   Parse & Extract (Silver Layer)
         ↓
Normalize & Enrich (Gold Layer - CSV outputs)
         ↓
   Streamlit Dashboard
```

### ML Models
- **Priority Model:** Rule-based weighted scoring
- **Duration Predictor:** Scikit-learn regression models
- **Scheduler:** Heuristic-based assignment algorithm

---

## 📁 Project Structure (MVP)

```
justicegraph/
│
├── frontend/
│   └── app.py                      # Streamlit dashboard (main MVP interface)
│
├── data/
│   └── gold/
│       ├── prioritized_cases.csv        # ML-scored cases
│       ├── optimized_schedule.csv       # Generated schedule
│       ├── case_duration_analysis.csv   # Duration metrics
│       └── backlog_trends.csv           # Court statistics
│
├── modeling/                       # ML modules (Phase 2)
│   ├── priority_model.py          # Case prioritization engine
│   └── duration_prediction.py     # Duration prediction models
│
├── visualization/                  # Chart generation
│   └── generate_visuals.py        # Plotly/Matplotlib utilities
│
├── utils/                         # Helper utilities
│   ├── db_utils.py               # Database operations
│   └── io_utils.py               # File I/O
│
├── run_mvp.py                     # Quick launcher script
├── generate_sample_data.py        # Sample data generator
├── requirements_mvp.txt           # Minimal dependencies
└── MVP_README.md                  # This file
```

---

## 🎬 Demo Workflow

### For Presentation/Demo:

1. **Open Terminal** and navigate to project:
   ```powershell
   cd C:\Users\rudra\Desktop\projects\justicegraph
   ```

2. **Launch MVP:**
   ```powershell
   python run_mvp.py
   ```

3. **Navigate through tabs:**
   - **Tab 1 (Analytics):** Show overall system metrics and trends
   - **Tab 2 (Prioritization):** Demonstrate filtering and case selection
   - **Tab 3 (Schedule):** Display optimized hearing calendar

4. **Key Talking Points:**
   - "This dashboard analyzes 150+ cases across 5 high courts"
   - "ML prioritization scores cases on a 0-100 scale using 5 factors"
   - "Optimized schedule balances workload across 6 judges over 20 days"
   - "High-priority cases (score > 70) are scheduled within 7 days"

5. **Interactive Features:**
   - Use filters to show specific courts or case types
   - Sort table by priority score (descending)
   - Download CSV exports to show data portability

---

## 🔧 Troubleshooting

### Common Issues

**Issue:** "ModuleNotFoundError: No module named 'streamlit'"
- **Solution:** Run `pip install -r requirements_mvp.txt`

**Issue:** "FileNotFoundError: prioritized_cases.csv"
- **Solution:** Run `python generate_sample_data.py` to create sample data

**Issue:** "Port 8501 already in use"
- **Solution:** Stop other Streamlit instances or use: `streamlit run frontend/app.py --server.port 8502`

**Issue:** Dashboard shows empty charts
- **Solution:** Check that CSV files exist in `data/gold/` directory

**Issue:** Slow loading on first run
- **Solution:** Normal - Streamlit caches data after first load

---

## 📊 Sample Data Statistics

The generated sample data includes:

- **150 cases** across 5 high courts (Delhi, Mumbai, Bangalore, Chennai, Kolkata)
- **6 case types** (Criminal, Civil, Writ, Appeal, Petition, Revision)
- **Case age range:** 30-730 days
- **Priority distribution:** 30% High, 50% Medium, 20% Low
- **Scheduled hearings:** 100+ hearings over 20 weekdays
- **6 judges** with balanced workload (15-20 hearings each)

---

## 🚀 Next Steps (Beyond MVP)

### Phase 3 Enhancements:
- **Real-time data ingestion** from court APIs
- **REST API** (FastAPI) for third-party integrations
- **User authentication** and role-based access
- **Advanced ML models** (XGBoost, neural networks)
- **Predictive alerts** for case delays
- **Mobile app** for judges and lawyers
- **Multi-language support** (Hindi, Tamil, etc.)

---

## 📝 Notes for Developers

### Extending the MVP:

1. **Add new visualizations:**
   - Edit `frontend/app.py`
   - Use Plotly Express for quick charts
   - Add to existing tabs or create new ones

2. **Connect to real database:**
   - Uncomment SQLAlchemy in `requirements_mvp.txt`
   - Replace CSV loading with database queries
   - Use `utils/db_utils.py` for connection management

3. **Integrate live ML models:**
   - Import from `modeling/priority_model.py`
   - Replace sample data with real predictions
   - Add model retraining interface

4. **Deploy to cloud:**
   - Use Streamlit Cloud (free tier)
   - Or containerize with Docker
   - Configure environment variables

---

## 📄 License

MIT License - See main README.md

---

## 👥 Contact

**Project:** JusticeGraph  
**Repository:** github.com/RudranshKaran/justicegraph  
**Maintainer:** Rudransh Karan

---

## ✅ Verification Checklist

Before demo/submission:

- [ ] Run `pip install -r requirements_mvp.txt` successfully
- [ ] Generate sample data with `python generate_sample_data.py`
- [ ] Verify 4 CSV files exist in `data/gold/`
- [ ] Launch dashboard with `python run_mvp.py`
- [ ] Open `http://localhost:8501` in browser
- [ ] Verify all 3 tabs load without errors
- [ ] Test filters in Prioritization tab
- [ ] Download CSV exports
- [ ] Check all charts render correctly

---

**🎉 You're ready to demo JusticeGraph MVP!**
