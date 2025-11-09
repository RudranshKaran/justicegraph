"""
Optimization Utilities

Helper functions for schedule optimization including validation,
efficiency calculation, and performance metrics.
"""

import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from typing import Dict, List, Tuple, Optional
import logging

from utils.logging_utils import get_logger

logger = get_logger(__name__)


def validate_schedule(
    schedule_df: pd.DataFrame,
    required_columns: Optional[List[str]] = None
) -> Tuple[bool, List[str]]:
    """
    Validate schedule DataFrame structure and data quality.
    
    Args:
        schedule_df: Schedule DataFrame
        required_columns: List of required column names
        
    Returns:
        Tuple of (is_valid, list of issues)
    """
    logger.info(f"Validating schedule with {len(schedule_df)} hearings")
    
    if required_columns is None:
        required_columns = [
            'case_id', 'judge_id', 'hearing_date',
            'case_number', 'judge_name'
        ]
    
    issues = []
    
    # Check if DataFrame is empty
    if schedule_df.empty:
        issues.append("Schedule is empty")
        return False, issues
    
    # Check required columns
    missing_cols = set(required_columns) - set(schedule_df.columns)
    if missing_cols:
        issues.append(f"Missing required columns: {missing_cols}")
    
    # Check for null values in critical columns
    for col in ['case_id', 'judge_id', 'hearing_date']:
        if col in schedule_df.columns:
            null_count = schedule_df[col].isnull().sum()
            if null_count > 0:
                issues.append(f"Column '{col}' has {null_count} null values")
    
    # Check for duplicate case assignments on same date
    if all(col in schedule_df.columns for col in ['case_id', 'hearing_date']):
        duplicates = schedule_df.duplicated(subset=['case_id', 'hearing_date'], keep=False)
        if duplicates.any():
            dup_count = duplicates.sum()
            issues.append(f"Found {dup_count} duplicate case-date assignments")
    
    # Check for past dates
    if 'hearing_date' in schedule_df.columns:
        today = datetime.now().date()
        past_dates = schedule_df[schedule_df['hearing_date'] < today]
        if not past_dates.empty:
            issues.append(f"Found {len(past_dates)} hearings scheduled in the past")
    
    # Check date range reasonableness (not more than 1 year out)
    if 'hearing_date' in schedule_df.columns:
        max_date = schedule_df['hearing_date'].max()
        one_year_out = datetime.now().date() + timedelta(days=365)
        if max_date > one_year_out:
            issues.append(f"Schedule extends beyond 1 year: {max_date}")
    
    is_valid = len(issues) == 0
    
    if is_valid:
        logger.info("✓ Schedule validation passed")
    else:
        logger.warning(f"✗ Schedule validation failed with {len(issues)} issues")
    
    return is_valid, issues


def calculate_efficiency(
    schedule_df: pd.DataFrame,
    cases_df: pd.DataFrame,
    judges_df: pd.DataFrame
) -> Dict[str, float]:
    """
    Calculate efficiency metrics for the schedule.
    
    Args:
        schedule_df: Scheduled hearings DataFrame
        cases_df: All pending cases DataFrame
        judges_df: Available judges DataFrame
        
    Returns:
        Dictionary of efficiency metrics
    """
    logger.info("Calculating schedule efficiency metrics")
    
    metrics = {}
    
    # Coverage: Percentage of cases scheduled
    total_cases = len(cases_df)
    scheduled_cases = schedule_df['case_id'].nunique()
    metrics['coverage_rate'] = round((scheduled_cases / total_cases) * 100, 2) if total_cases > 0 else 0
    
    # Utilization: Average judge utilization
    total_judges = len(judges_df)
    judges_assigned = schedule_df['judge_id'].nunique()
    metrics['judge_utilization'] = round((judges_assigned / total_judges) * 100, 2) if total_judges > 0 else 0
    
    # Daily load: Average hearings per day
    days_scheduled = schedule_df['hearing_date'].nunique()
    metrics['avg_hearings_per_day'] = round(len(schedule_df) / days_scheduled, 2) if days_scheduled > 0 else 0
    
    # Judge workload balance: Standard deviation of hearings per judge
    hearings_per_judge = schedule_df.groupby('judge_id').size()
    metrics['workload_std_dev'] = round(hearings_per_judge.std(), 2) if len(hearings_per_judge) > 0 else 0
    metrics['avg_hearings_per_judge'] = round(hearings_per_judge.mean(), 2) if len(hearings_per_judge) > 0 else 0
    
    # Priority scheduling: Average priority of scheduled cases
    if 'priority_score' in schedule_df.columns:
        metrics['avg_priority_scheduled'] = round(schedule_df['priority_score'].mean(), 2)
        
        # High priority scheduling rate (priority >= 70)
        high_priority_scheduled = (schedule_df['priority_score'] >= 70).sum()
        if 'priority_score' in cases_df.columns:
            high_priority_total = (cases_df['priority_score'] >= 70).sum()
            if high_priority_total > 0:
                metrics['high_priority_coverage'] = round(
                    (high_priority_scheduled / high_priority_total) * 100, 2
                )
    
    # Time efficiency: Average days until first hearing
    if 'hearing_date' in schedule_df.columns:
        today = datetime.now().date()
        earliest_hearings = schedule_df.groupby('case_id')['hearing_date'].min()
        days_to_hearing = [(h - today).days for h in earliest_hearings]
        metrics['avg_days_to_hearing'] = round(np.mean(days_to_hearing), 2) if days_to_hearing else 0
    
    # Schedule density: Percentage of available slots used
    if 'hearing_date' in schedule_df.columns and days_scheduled > 0:
        # Assuming 20 hearings per day capacity
        capacity_per_day = 20
        total_capacity = days_scheduled * capacity_per_day
        metrics['slot_utilization'] = round((len(schedule_df) / total_capacity) * 100, 2)
    
    logger.info(f"Calculated {len(metrics)} efficiency metrics")
    return metrics


def calculate_improvement_metrics(
    new_schedule_df: pd.DataFrame,
    old_schedule_df: pd.DataFrame
) -> Dict[str, float]:
    """
    Compare new schedule against previous schedule.
    
    Args:
        new_schedule_df: New optimized schedule
        old_schedule_df: Previous schedule
        
    Returns:
        Dictionary of improvement metrics
    """
    logger.info("Calculating improvement metrics")
    
    improvements = {}
    
    # More cases scheduled
    old_cases = old_schedule_df['case_id'].nunique() if not old_schedule_df.empty else 0
    new_cases = new_schedule_df['case_id'].nunique()
    improvements['cases_increase'] = new_cases - old_cases
    improvements['cases_increase_pct'] = round(
        ((new_cases - old_cases) / old_cases) * 100, 2
    ) if old_cases > 0 else 0
    
    # Better priority coverage
    if 'priority_score' in new_schedule_df.columns and 'priority_score' in old_schedule_df.columns:
        old_avg_priority = old_schedule_df['priority_score'].mean() if not old_schedule_df.empty else 0
        new_avg_priority = new_schedule_df['priority_score'].mean()
        improvements['priority_improvement'] = round(new_avg_priority - old_avg_priority, 2)
    
    # More balanced workload
    if 'judge_id' in new_schedule_df.columns and 'judge_id' in old_schedule_df.columns:
        old_std = old_schedule_df.groupby('judge_id').size().std() if not old_schedule_df.empty else 0
        new_std = new_schedule_df.groupby('judge_id').size().std()
        improvements['workload_balance_improvement'] = round(old_std - new_std, 2)
    
    logger.info("Improvement metrics calculated")
    return improvements


def analyze_workload_distribution(schedule_df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze workload distribution across judges.
    
    Args:
        schedule_df: Schedule DataFrame
        
    Returns:
        DataFrame with workload statistics per judge
    """
    logger.info("Analyzing workload distribution")
    
    if schedule_df.empty or 'judge_id' not in schedule_df.columns:
        return pd.DataFrame()
    
    # Group by judge
    workload = schedule_df.groupby(['judge_id', 'judge_name']).agg({
        'case_id': 'count',
        'hearing_date': lambda x: x.nunique()
    }).reset_index()
    
    workload.columns = ['judge_id', 'judge_name', 'total_hearings', 'days_scheduled']
    
    # Calculate average per day
    workload['avg_hearings_per_day'] = (
        workload['total_hearings'] / workload['days_scheduled']
    ).round(2)
    
    # Add priority info if available
    if 'priority_score' in schedule_df.columns:
        priority_avg = schedule_df.groupby('judge_id')['priority_score'].mean()
        workload['avg_priority'] = workload['judge_id'].map(priority_avg).round(2)
    
    # Sort by total hearings
    workload = workload.sort_values('total_hearings', ascending=False)
    
    logger.info(f"Analyzed workload for {len(workload)} judges")
    return workload


def identify_scheduling_gaps(
    schedule_df: pd.DataFrame,
    start_date: date,
    end_date: date
) -> pd.DataFrame:
    """
    Identify dates with low utilization or gaps.
    
    Args:
        schedule_df: Schedule DataFrame
        start_date: Start of scheduling period
        end_date: End of scheduling period
        
    Returns:
        DataFrame with daily utilization
    """
    logger.info(f"Identifying scheduling gaps from {start_date} to {end_date}")
    
    # Create date range
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    date_range = [d.date() for d in date_range if d.weekday() < 5]  # Exclude weekends
    
    # Count hearings per day
    if not schedule_df.empty and 'hearing_date' in schedule_df.columns:
        daily_counts = schedule_df.groupby('hearing_date').size()
    else:
        daily_counts = pd.Series(dtype=int)
    
    # Create utilization DataFrame
    utilization = pd.DataFrame({
        'date': date_range,
        'hearings_scheduled': [daily_counts.get(d, 0) for d in date_range]
    })
    
    # Add utilization percentage (assuming 20 hearings capacity)
    utilization['utilization_pct'] = (utilization['hearings_scheduled'] / 20 * 100).round(2)
    
    # Flag under-utilized days
    utilization['is_underutilized'] = utilization['utilization_pct'] < 50
    
    # Add day of week
    utilization['day_of_week'] = pd.to_datetime(utilization['date']).dt.day_name()
    
    logger.info(f"Analyzed {len(utilization)} days")
    return utilization


def generate_schedule_report(
    schedule_df: pd.DataFrame,
    efficiency_metrics: Dict[str, float],
    workload_df: pd.DataFrame,
    output_path: str = "reports/SCHEDULER_RESULTS.md"
) -> None:
    """
    Generate comprehensive schedule optimization report.
    
    Args:
        schedule_df: Optimized schedule
        efficiency_metrics: Efficiency metrics dictionary
        workload_df: Workload distribution DataFrame
        output_path: Path to save report
    """
    logger.info(f"Generating schedule report at {output_path}")
    
    report = []
    report.append("# Hearing Schedule Optimization Report\n\n")
    report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    # Summary statistics
    report.append("## Schedule Summary\n\n")
    report.append(f"- **Total Hearings Scheduled:** {len(schedule_df)}\n")
    report.append(f"- **Unique Cases:** {schedule_df['case_id'].nunique()}\n")
    report.append(f"- **Judges Assigned:** {schedule_df['judge_id'].nunique()}\n")
    report.append(f"- **Days Scheduled:** {schedule_df['hearing_date'].nunique()}\n")
    report.append(f"- **Date Range:** {schedule_df['hearing_date'].min()} to {schedule_df['hearing_date'].max()}\n\n")
    
    # Efficiency metrics
    report.append("## Efficiency Metrics\n\n")
    for metric, value in efficiency_metrics.items():
        metric_name = metric.replace('_', ' ').title()
        report.append(f"- **{metric_name}:** {value}\n")
    report.append("\n")
    
    # Workload distribution
    report.append("## Workload Distribution\n\n")
    report.append("| Judge | Total Hearings | Days Scheduled | Avg Per Day |\n")
    report.append("|-------|----------------|----------------|-------------|\n")
    for _, row in workload_df.head(10).iterrows():
        report.append(
            f"| {row['judge_name']} | {row['total_hearings']} | "
            f"{row['days_scheduled']} | {row['avg_hearings_per_day']} |\n"
        )
    report.append("\n")
    
    # Daily distribution
    report.append("## Daily Hearing Distribution\n\n")
    daily_dist = schedule_df.groupby('hearing_date').size().reset_index(name='hearings')
    report.append("| Date | Hearings |\n")
    report.append("|------|----------|\n")
    for _, row in daily_dist.head(14).iterrows():
        report.append(f"| {row['hearing_date']} | {row['hearings']} |\n")
    
    # Write report
    from pathlib import Path
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(''.join(report))
    
    logger.info(f"Report saved to {output_path}")


if __name__ == "__main__":
    # Example usage
    logger.info("Optimization utilities module loaded")
    print("✓ Optimization utilities ready")
