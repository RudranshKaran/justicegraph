# -*- coding: utf-8 -*-
"""
Generate Sample Data for JusticeGraph MVP

Creates realistic mock data for demonstration purposes.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
GOLD_DIR = PROJECT_ROOT / 'data' / 'gold'


def ensure_directory():
    """Ensure gold directory exists."""
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✓ Gold directory: {GOLD_DIR}")


def generate_prioritized_cases(num_cases=150):
    """Generate prioritized cases dataset."""
    print(f"\n📊 Generating {num_cases} prioritized cases...")
    
    np.random.seed(42)
    
    case_types = ['Criminal', 'Civil', 'Writ', 'Appeal', 'Petition', 'Revision']
    courts = ['Delhi HC', 'Mumbai HC', 'Bangalore HC', 'Chennai HC', 'Kolkata HC']
    statuses = ['Pending', 'Listed', 'Adjourned', 'Part Heard']
    
    # Generate filing dates over past 2 years
    base_date = datetime.now() - timedelta(days=730)
    filing_dates = [base_date + timedelta(days=np.random.randint(0, 730)) for _ in range(num_cases)]
    
    data = {
        'case_id': range(1, num_cases + 1),
        'case_number': [
            f"{np.random.choice(['CRL.A', 'CIV.A', 'WRIT', 'APP', 'REV'])}/{i}/202{np.random.randint(2,4)}" 
            for i in range(1, num_cases + 1)
        ],
        'court_code': np.random.choice(courts, num_cases),
        'case_type': np.random.choice(case_types, num_cases),
        'case_status': np.random.choice(statuses, num_cases),
        'filing_date': filing_dates,
        'petitioner': [f"Petitioner {i}" for i in range(1, num_cases + 1)],
        'respondent': [f"Respondent {i}" for i in range(1, num_cases + 1)],
    }
    
    df = pd.DataFrame(data)
    
    # Calculate age in days
    df['age_days'] = (datetime.now() - pd.to_datetime(df['filing_date'])).dt.days
    
    # Generate hearing counts (more hearings for older cases)
    df['hearing_count'] = np.maximum(1, (df['age_days'] / 90).astype(int) + np.random.randint(-2, 5, num_cases))
    df['hearing_count'] = df['hearing_count'].clip(lower=0)
    
    # Calculate priority scores based on multiple factors
    # Age factor (0-30 points)
    age_score = (df['age_days'] / df['age_days'].max() * 30).clip(upper=30)
    
    # Case type factor (0-25 points)
    case_type_scores = {
        'Criminal': 25, 'Writ': 22, 'Appeal': 18, 
        'Revision': 15, 'Petition': 15, 'Civil': 12
    }
    type_score = df['case_type'].map(case_type_scores)
    
    # Hearing count factor (0-20 points)
    hearing_score = (df['hearing_count'] / df['hearing_count'].max() * 20).clip(upper=20)
    
    # Court workload factor (0-15 points) - simplified random
    workload_score = np.random.uniform(5, 15, num_cases)
    
    # Urgency factor (0-10 points) - random
    urgency_score = np.random.uniform(0, 10, num_cases)
    
    # Total priority score
    df['priority_score'] = (age_score + type_score + hearing_score + workload_score + urgency_score).round(2)
    df['priority_score'] = df['priority_score'].clip(lower=20, upper=100)
    
    # Priority categories
    df['priority_category'] = pd.cut(
        df['priority_score'],
        bins=[0, 50, 70, 100],
        labels=['Low', 'Medium', 'High']
    )
    
    # Format filing date
    df['filing_date'] = df['filing_date'].dt.strftime('%Y-%m-%d')
    
    # Save to CSV
    output_path = GOLD_DIR / 'prioritized_cases.csv'
    df.to_csv(output_path, index=False)
    print(f"✓ Saved: {output_path}")
    
    return df


def generate_optimized_schedule(prioritized_cases_df, num_days=20):
    """Generate optimized hearing schedule."""
    print(f"\n📅 Generating {num_days}-day optimized schedule...")
    
    np.random.seed(42)
    
    judges = [
        'Justice A. Kumar',
        'Justice B. Singh',
        'Justice C. Patel',
        'Justice D. Sharma',
        'Justice E. Reddy',
        'Justice F. Gupta'
    ]
    
    # Get high and medium priority cases
    high_priority = prioritized_cases_df[prioritized_cases_df['priority_score'] > 70].copy()
    medium_priority = prioritized_cases_df[
        (prioritized_cases_df['priority_score'] >= 50) & 
        (prioritized_cases_df['priority_score'] <= 70)
    ].copy()
    
    # Select cases to schedule (prioritize high priority)
    cases_to_schedule = pd.concat([
        high_priority.sample(min(len(high_priority), 60)),
        medium_priority.sample(min(len(medium_priority), 40))
    ])
    
    schedules = []
    start_date = datetime.now() + timedelta(days=1)
    
    case_idx = 0
    for day in range(num_days):
        hearing_date = start_date + timedelta(days=day)
        
        # Skip weekends
        if hearing_date.weekday() >= 5:
            continue
        
        # Assign 5-8 hearings per judge per day
        for judge in judges:
            num_hearings = np.random.randint(5, 9)
            
            for _ in range(num_hearings):
                if case_idx >= len(cases_to_schedule):
                    break
                
                case = cases_to_schedule.iloc[case_idx]
                
                schedules.append({
                    'case_id': case['case_id'],
                    'case_number': case['case_number'],
                    'case_type': case['case_type'],
                    'judge_name': judge,
                    'hearing_date': hearing_date.strftime('%Y-%m-%d'),
                    'priority_score': case['priority_score'],
                    'estimated_duration_hours': 0.5,
                    'session': np.random.choice(['Morning', 'Afternoon'])
                })
                
                case_idx += 1
            
            if case_idx >= len(cases_to_schedule):
                break
        
        if case_idx >= len(cases_to_schedule):
            break
    
    schedule_df = pd.DataFrame(schedules)
    
    # Save to CSV
    output_path = GOLD_DIR / 'optimized_schedule.csv'
    schedule_df.to_csv(output_path, index=False)
    print(f"✓ Saved: {output_path}")
    print(f"  Total hearings scheduled: {len(schedule_df)}")
    
    return schedule_df


def generate_case_duration_analysis():
    """Generate case duration analysis dataset."""
    print("\n⏱️ Generating case duration analysis...")
    
    case_types = ['Criminal', 'Civil', 'Writ', 'Appeal', 'Petition', 'Revision']
    
    data = {
        'case_type': case_types,
        'total_cases': [145, 128, 89, 76, 62, 45],
        'avg_duration_days': [420, 650, 380, 510, 590, 480],
        'median_duration_days': [365, 580, 320, 450, 520, 410],
        'min_duration_days': [90, 120, 80, 110, 95, 105],
        'max_duration_days': [1250, 1580, 980, 1340, 1420, 1180],
        'std_duration_days': [185, 245, 165, 205, 225, 195],
        'delayed_cases': [42, 56, 28, 35, 38, 22],
        'disposal_rate_pct': [68.5, 54.2, 75.3, 62.8, 58.9, 65.4]
    }
    
    df = pd.DataFrame(data)
    
    # Save to CSV
    output_path = GOLD_DIR / 'case_duration_analysis.csv'
    df.to_csv(output_path, index=False)
    print(f"✓ Saved: {output_path}")
    
    return df


def generate_backlog_trends():
    """Generate backlog trends dataset."""
    print("\n📈 Generating backlog trends...")
    
    courts = ['Delhi HC', 'Mumbai HC', 'Bangalore HC', 'Chennai HC', 'Kolkata HC']
    
    data = {
        'court_code': courts,
        'pending_cases': [3250, 4120, 2890, 3560, 3180],
        'disposed_cases_last_month': [245, 298, 215, 267, 238],
        'new_cases_last_month': [312, 378, 268, 324, 295],
        'disposal_rate_pct': [67.5, 58.3, 71.2, 64.8, 69.1],
        'avg_case_age_days': [485, 562, 428, 512, 475],
        'backlog_severity_score': [72.5, 84.3, 65.8, 76.2, 71.9],
        'judges_count': [35, 42, 28, 38, 32]
    }
    
    df = pd.DataFrame(data)
    
    # Calculate cases per judge
    df['cases_per_judge'] = (df['pending_cases'] / df['judges_count']).round(1)
    
    # Save to CSV
    output_path = GOLD_DIR / 'backlog_trends.csv'
    df.to_csv(output_path, index=False)
    print(f"✓ Saved: {output_path}")
    
    return df


def main():
    """Generate all sample datasets."""
    print("\n" + "=" * 60)
    print("  JUSTICEGRAPH - SAMPLE DATA GENERATOR")
    print("=" * 60)
    
    # Ensure directory exists
    ensure_directory()
    
    # Generate datasets
    prioritized_cases = generate_prioritized_cases(150)
    schedule = generate_optimized_schedule(prioritized_cases, 20)
    case_analysis = generate_case_duration_analysis()
    backlog_trends = generate_backlog_trends()
    
    print("\n" + "=" * 60)
    print("  ✅ ALL SAMPLE DATA GENERATED SUCCESSFULLY")
    print("=" * 60)
    print(f"\n📁 Location: {GOLD_DIR}")
    print(f"\n📊 Files created:")
    print(f"  • prioritized_cases.csv ({len(prioritized_cases)} rows)")
    print(f"  • optimized_schedule.csv ({len(schedule)} rows)")
    print(f"  • case_duration_analysis.csv ({len(case_analysis)} rows)")
    print(f"  • backlog_trends.csv ({len(backlog_trends)} rows)")
    print("\n💡 Ready to run: python run_mvp.py\n")


if __name__ == "__main__":
    main()
