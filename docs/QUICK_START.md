# JusticeGraph MVP - Quick Reference Guide

## 🚀 Three Ways to Launch

### Option 1: Automated Setup (Recommended for First Time)
```powershell
python setup_mvp.py
```
This will:
- Check Python version
- Install all dependencies
- Generate sample data
- Launch dashboard automatically

### Option 2: Manual Setup
```powershell
# Step 1: Install dependencies
pip install -r requirements_mvp.txt

# Step 2: Generate data
python generate_sample_data.py

# Step 3: Launch
python run_mvp.py
```

### Option 3: Direct Launch (If already set up)
```powershell
streamlit run frontend/app.py
```

---

## 📊 Dashboard Navigation

### Tab 1: Analytics Dashboard
- **Purpose:** System-wide overview
- **Key Metrics:** Total cases, avg priority, high priority count, avg age
- **Charts:** 
  - Case type distribution (pie)
  - Priority distribution (histogram)
  - Court workload (bar)
  - Case age by type (box plot)

### Tab 2: Case Prioritization
- **Purpose:** Identify urgent cases
- **Features:**
  - Filter by court, case type, priority
  - Sortable table with top 50 cases
  - CSV export
- **Score Range:** 0-100 (High > 70, Medium 50-70, Low < 50)

### Tab 3: Optimized Schedule
- **Purpose:** View AI-generated hearing calendar
- **Features:**
  - Timeline chart (hearings per day)
  - Judge workload distribution
  - Detailed schedule table
  - CSV export

---

## 🔍 Demo Tips

### For Presentation:

1. **Start with Analytics Tab**
   - Point out total case count
   - Highlight high priority percentage
   - Explain case type distribution

2. **Move to Prioritization Tab**
   - Use filters to show specific court
   - Sort by priority score (descending)
   - Explain scoring factors (age, type, hearings)

3. **Show Schedule Tab**
   - Demonstrate balanced workload
   - Point out priority-based scheduling
   - Export schedule for stakeholders

### Key Talking Points:

- "Analyzed 150 cases across 5 major high courts"
- "ML prioritization uses 5 factors with weighted scoring"
- "Optimized schedule balances 6 judges over 20 days"
- "High-priority cases scheduled within first week"
- "Interactive filters for real-time insights"

---

## 📁 File Locations

### Generated Data (data/gold/):
- `prioritized_cases.csv` - 150 cases with ML scores
- `optimized_schedule.csv` - 100+ scheduled hearings
- `case_duration_analysis.csv` - Duration metrics
- `backlog_trends.csv` - Court statistics

### Dashboard Code:
- `frontend/app.py` - Main Streamlit interface

### Utilities:
- `generate_sample_data.py` - Data generator
- `run_mvp.py` - Quick launcher
- `setup_mvp.py` - Automated setup

---

## ⚡ Quick Commands

```powershell
# Generate fresh sample data
python generate_sample_data.py

# Launch dashboard
python run_mvp.py

# Install single package
pip install streamlit

# Check installed packages
pip list | Select-String "streamlit|plotly|pandas"

# Update package
pip install --upgrade streamlit
```

---

## 🐛 Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| Module not found | `pip install -r requirements_mvp.txt` |
| Port in use | Use `streamlit run frontend/app.py --server.port 8502` |
| No data files | Run `python generate_sample_data.py` |
| Slow first load | Normal - caching improves subsequent loads |
| Chart not showing | Check CSV file exists in data/gold/ |

---

## 📈 Performance Notes

- **Startup time:** 3-5 seconds
- **Data load time:** < 1 second (cached)
- **Chart render time:** < 2 seconds
- **Memory usage:** ~150MB
- **Browser:** Chrome/Edge/Firefox recommended

---

## 🎯 Success Checklist

Before demo:
- [ ] Dashboard loads at http://localhost:8501
- [ ] All 3 tabs visible
- [ ] Metrics display correctly
- [ ] Charts render properly
- [ ] Filters work in Tab 2
- [ ] CSV export downloads
- [ ] No error messages

---

## 📞 Support

Check main documentation:
- `MVP_README.md` - Complete setup guide
- `README.md` - Full project overview
- `PHASE2_SUMMARY.md` - Technical details

---

**Last Updated:** November 2025  
**Version:** MVP 1.0
