# JusticeGraph Phase 2 - Quick Start Guide

This guide will help you quickly set up and run Phase 2 analytics and optimization features.

---

## Prerequisites

✅ Phase 1 completed (database populated with judicial data)  
✅ Python 3.8+ installed  
✅ Virtual environment activated  

---

## Installation

### 1. Install Phase 2 Dependencies

```bash
# Install all requirements including Phase 2 packages
pip install -r requirements.txt

# Key Phase 2 packages:
# - scikit-learn (ML models)
# - xgboost (gradient boosting)
# - matplotlib, seaborn, plotly (visualizations)
# - ortools (optimization - optional but recommended)
# - jupyter (notebooks)
```

### 2. Install OR-Tools (Optional but Recommended)

For optimal hearing scheduling:

```bash
pip install ortools
```

*Note: Without OR-Tools, the system will use heuristic scheduling (still functional).*

---

## Quick Start: 5-Minute Tour

### 1. Analyze Case Durations

```python
from analysis.case_duration_analysis import analyze_case_durations, get_duration_statistics

# Analyze all cases
duration_df = analyze_case_durations()
print(f"Analyzed {len(duration_df)} cases")

# Get statistics by case type
stats = get_duration_statistics(duration_df, group_by='case_type')
print("\nCase Duration Statistics:")
print(stats)

# Find delayed cases (>365 days)
from analysis.case_duration_analysis import identify_delayed_cases
delayed = identify_delayed_cases(duration_df, threshold_days=365)
print(f"\nFound {len(delayed)} delayed cases")
```

### 2. Analyze Backlog Trends

```python
from analysis.backlog_trends import (
    analyze_backlog_trends,
    calculate_disposal_rate,
    identify_backlog_hotspots
)

# Analyze backlog
backlog_df = analyze_backlog_trends()

# Calculate disposal rates
disposal_df = calculate_disposal_rate(time_period_months=12)
print("\nTop 5 Courts by Disposal Rate:")
print(disposal_df.head())

# Identify hotspots
hotspots = identify_backlog_hotspots(backlog_df)
print(f"\nBacklog Hotspots: {len(hotspots)} courts need attention")
```

### 3. Calculate Case Priorities

```python
from modeling.priority_model import calculate_priority_scores, export_prioritized_cases

# Calculate priority scores for all pending cases
priority_df = calculate_priority_scores()
print(f"\nPrioritized {len(priority_df)} cases")

# View top 10 high-priority cases
print("\nTop 10 High-Priority Cases:")
print(priority_df[['case_number', 'case_type', 'priority_score', 'priority_category']].head(10))

# Export to CSV
export_prioritized_cases(priority_df, "data/gold/prioritized_cases.csv")
print("\n✓ Saved to data/gold/prioritized_cases.csv")
```

### 4. Train Duration Prediction Model

```python
from modeling.duration_prediction import train_and_evaluate_models, generate_duration_report

# Train and compare all models (Linear, RF, GB, XGBoost)
results = train_and_evaluate_models()

# View results
for model_type, metrics in results.items():
    print(f"\n{model_type.upper()}:")
    print(f"  MAE: {metrics.get('mae', 'N/A')} days")
    print(f"  R²: {metrics.get('r2', 'N/A')}")

# Generate report
generate_duration_report(results, "reports/MODEL_METRICS.md")
print("\n✓ Model report saved to reports/MODEL_METRICS.md")
```

### 5. Generate Optimized Schedule

```python
from optimization.scheduler import generate_optimal_schedule, export_schedule

# Generate 2-week schedule
schedule = generate_optimal_schedule(
    court_code=None,  # All courts (or specify like 'DL-HC')
    num_days=14,
    use_optimization=True  # Use OR-Tools if available
)

print(f"\nScheduled {len(schedule)} hearings")
print("\nDaily distribution:")
print(schedule.groupby('hearing_date').size())

# Export schedule
export_schedule(schedule, "data/gold/optimized_schedule.csv")
print("\n✓ Schedule saved to data/gold/optimized_schedule.csv")
```

### 6. Generate Visualizations

```python
from visualization.generate_visuals import generate_all_visuals

# Generate all charts and plots
generate_all_visuals(output_dir="visualization/outputs")

print("\n✓ All visualizations saved to visualization/outputs/")
print("  Open the .html files in your browser to view interactive charts")
```

---

## Running the EDA Notebook

### Start Jupyter Notebook

```bash
# From project root
jupyter notebook analysis/eda_overview.ipynb
```

The notebook includes:
- Data loading and validation
- Statistical summaries
- Interactive visualizations
- Correlation analysis
- Trend identification

---

## Common Workflows

### Workflow 1: Daily Priority Update

```python
# daily_priority_update.py
from modeling.priority_model import calculate_priority_scores, update_case_priorities_in_db

# Calculate new priorities
priority_df = calculate_priority_scores()

# Update database
updated_count = update_case_priorities_in_db(priority_df)
print(f"Updated {updated_count} case priorities")
```

### Workflow 2: Weekly Schedule Generation

```python
# weekly_schedule.py
from optimization.scheduler import generate_optimal_schedule
from optimization.constraint_builder import create_default_constraints
import datetime

# Create constraints
constraints = create_default_constraints()

# Generate next week's schedule
start_date = datetime.date.today() + datetime.timedelta(days=7)
schedule = generate_optimal_schedule(
    start_date=start_date,
    num_days=7
)

# Validate
is_valid, violations = constraints.validate_schedule(schedule, judges_df)
if is_valid:
    print("✓ Schedule is valid")
else:
    print(f"✗ {len(violations)} constraint violations")
```

### Workflow 3: Monthly Analytics Report

```python
# monthly_report.py
from analysis.case_duration_analysis import analyze_case_durations, export_duration_analysis
from analysis.backlog_trends import analyze_backlog_trends, export_backlog_analysis
from analysis.court_performance import analyze_court_performance, export_performance_analysis
from datetime import datetime, timedelta

# Set date range (last month)
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

# Run analyses
duration_df = analyze_case_durations(start_date=start_date, end_date=end_date)
backlog_df = analyze_backlog_trends(start_date=start_date, end_date=end_date)
performance_df = analyze_court_performance(time_period_months=1)

# Export all
export_duration_analysis(duration_df, "reports/monthly_duration.csv")
export_backlog_analysis(backlog_df, "reports/monthly_backlog.csv")
export_performance_analysis(performance_df, "reports/monthly_performance.csv")

print("✓ Monthly reports generated")
```

---

## Validation & Testing

### Test Priority Model

```python
from modeling.priority_model import CasePrioritizer

# Create prioritizer
prioritizer = CasePrioritizer()

# Test case
test_case = {
    'filing_date': datetime(2020, 1, 1),  # 5 years old
    'case_type': 'criminal',
    'hearing_count': 15,
    'subject_matter': 'bail application'
}

# Calculate score
score = prioritizer.calculate_priority_score(test_case, court_workload=500)
print(f"Priority Score: {score}")
# Expected: High score (70-80+) due to age, type, and urgency
```

### Test Scheduler

```python
from optimization.scheduler import HearingScheduler
import pandas as pd

# Create test data
cases_df = pd.DataFrame({
    'case_id': [1, 2, 3],
    'case_number': ['CRL/1/2024', 'CIV/2/2024', 'WRT/3/2024'],
    'priority_score': [85, 60, 90]
})

judges_df = pd.DataFrame({
    'judge_id': [1, 2],
    'judge_name': ['Justice A', 'Justice B']
})

# Schedule
scheduler = HearingScheduler()
schedule = scheduler.schedule_hearings_heuristic(
    cases_df, judges_df,
    start_date=datetime.now().date(),
    num_days=7
)

print(f"Scheduled {len(schedule)} hearings")
```

---

## Configuration

### Custom Priority Weights

```python
from modeling.priority_model import CasePrioritizer

# Custom weights
custom_weights = {
    'age': 0.40,          # Increase age importance
    'case_type': 0.30,
    'hearing_count': 0.15,
    'court_workload': 0.10,
    'urgency_factors': 0.05
}

prioritizer = CasePrioritizer(weights=custom_weights)
```

### Custom Constraints

```python
from optimization.constraint_builder import ConstraintBuilder

builder = ConstraintBuilder()
builder.add_max_hearings_per_day(25) \  # Increase capacity
       .add_max_hearings_per_judge(20) \
       .add_priority_deadline(80.0, 5) \  # Urgent cases within 5 days
       .add_no_weekend_scheduling()

# Add holidays
from datetime import date
holidays = [date(2025, 12, 25), date(2026, 1, 1)]
builder.add_holiday_exclusion(holidays)
```

---

## Troubleshooting

### Issue: "No module named 'ortools'"

**Solution:**
```bash
pip install ortools
```
Or run scheduler with `use_optimization=False` for heuristic mode.

### Issue: "get_db_session is not defined"

**Solution:** Ensure `utils/db_utils.py` has the `get_db_session()` function:

```python
# In utils/db_utils.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def get_db_session():
    engine = create_engine(DATABASE_URI)  # Your DB URI
    Session = sessionmaker(bind=engine)
    return Session()
```

### Issue: "No cases found"

**Solution:** Ensure Phase 1 is complete and database is populated:

```python
from sqlalchemy import create_engine
from models.data_models import Case, Base

engine = create_engine(DATABASE_URI)
session = sessionmaker(bind=engine)()

# Check case count
case_count = session.query(Case).count()
print(f"Total cases in database: {case_count}")
```

### Issue: Memory errors with large datasets

**Solution:** Use batch processing:

```python
# Process courts individually
court_codes = ['DL-HC', 'MH-HC', 'KA-HC']  # Example

for court_code in court_codes:
    schedule = generate_optimal_schedule(
        court_code=court_code,
        num_days=14
    )
    export_schedule(schedule, f"data/gold/schedule_{court_code}.csv")
```

---

## Performance Tips

1. **Use Indices:** Ensure database has indices on:
   - `cases.filing_date`
   - `cases.case_status`
   - `cases.is_pending`
   - `cases.court_id`

2. **Batch Processing:** For large courts (1000+ cases), process in batches

3. **Caching:** Cache frequently used DataFrames:
   ```python
   import joblib
   
   # Save
   joblib.dump(duration_df, 'cache/duration_df.pkl')
   
   # Load
   duration_df = joblib.load('cache/duration_df.pkl')
   ```

4. **Parallel Processing:** Use multiple cores for model training:
   ```python
   from sklearn.ensemble import RandomForestRegressor
   
   model = RandomForestRegressor(n_jobs=-1)  # Use all cores
   ```

---

## Next Steps

1. **Explore the EDA Notebook:** Open `analysis/eda_overview.ipynb`
2. **Review Reports:** Check `reports/` directory for generated summaries
3. **Visualizations:** Browse `visualization/outputs/` for charts
4. **Customize Models:** Tune hyperparameters in `modeling/` modules
5. **Schedule Optimization:** Experiment with different constraints

---

## Getting Help

- **Documentation:** See `documentation/` folder
- **Examples:** Check `__main__` sections in each module
- **Phase 2 Summary:** Read `PHASE2_SUMMARY.md` for comprehensive overview

---

## Quick Command Reference

```bash
# Install dependencies
pip install -r requirements.txt

# Start Jupyter
jupyter notebook

# Python quick tests
python -m analysis.case_duration_analysis
python -m modeling.priority_model
python -m modeling.duration_prediction
python -m optimization.scheduler
python -m visualization.generate_visuals

# Run specific analysis
python -c "from analysis.backlog_trends import analyze_backlog_trends; df = analyze_backlog_trends(); print(df.head())"

# Generate schedule
python -c "from optimization.scheduler import generate_optimal_schedule; s = generate_optimal_schedule(num_days=7); print(f'{len(s)} hearings scheduled')"
```

---

**Ready to explore Phase 2!** 🚀

Start with the EDA notebook or run the Quick Start examples above.
