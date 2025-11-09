"""
Case Duration Analysis Module

This module analyzes case duration patterns, including:
- Average duration by case type
- Distribution of case ages
- Factors affecting case duration
- Duration trends over time
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from models.data_models import Case, Hearing, Court, CaseType, CaseStatus
from utils.logging_utils import get_logger
from utils.db_utils import get_db_session

logger = get_logger(__name__)


def calculate_case_age(filing_date: datetime, reference_date: Optional[datetime] = None) -> int:
    """
    Calculate the age of a case in days.
    
    Args:
        filing_date: Date when the case was filed
        reference_date: Reference date (defaults to today)
        
    Returns:
        Age of the case in days
    """
    if filing_date is None:
        return None
    
    ref_date = reference_date or datetime.now()
    return (ref_date - filing_date).days


def analyze_case_durations(
    db_session: Optional[Session] = None,
    court_code: Optional[str] = None,
    case_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> pd.DataFrame:
    """
    Analyze case durations across different dimensions.
    
    Args:
        db_session: Database session (creates one if not provided)
        court_code: Filter by specific court code
        case_type: Filter by case type
        start_date: Filter cases filed after this date
        end_date: Filter cases filed before this date
        
    Returns:
        DataFrame with duration analysis results
    """
    logger.info("Starting case duration analysis")
    
    close_session = False
    if db_session is None:
        db_session = get_db_session()
        close_session = True
    
    try:
        # Build query with filters
        query = db_session.query(
            Case.case_id,
            Case.case_number,
            Case.case_type,
            Case.case_status,
            Case.filing_date,
            Case.disposal_date,
            Case.first_hearing_date,
            Case.last_hearing_date,
            Court.court_code,
            Court.court_name,
            Court.state,
            func.count(Hearing.hearing_id).label('hearing_count')
        ).join(Court, Case.court_id == Court.court_id
        ).outerjoin(Hearing, Case.case_id == Hearing.case_id
        ).group_by(
            Case.case_id,
            Case.case_number,
            Case.case_type,
            Case.case_status,
            Case.filing_date,
            Case.disposal_date,
            Case.first_hearing_date,
            Case.last_hearing_date,
            Court.court_code,
            Court.court_name,
            Court.state
        )
        
        # Apply filters
        if court_code:
            query = query.filter(Court.court_code == court_code)
        if case_type:
            query = query.filter(Case.case_type == case_type)
        if start_date:
            query = query.filter(Case.filing_date >= start_date)
        if end_date:
            query = query.filter(Case.filing_date <= end_date)
        
        # Execute query and convert to DataFrame
        results = query.all()
        
        if not results:
            logger.warning("No cases found matching the criteria")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame([
            {
                'case_id': r.case_id,
                'case_number': r.case_number,
                'case_type': r.case_type.value if r.case_type else None,
                'case_status': r.case_status.value if r.case_status else None,
                'filing_date': r.filing_date,
                'disposal_date': r.disposal_date,
                'first_hearing_date': r.first_hearing_date,
                'last_hearing_date': r.last_hearing_date,
                'court_code': r.court_code,
                'court_name': r.court_name,
                'state': r.state,
                'hearing_count': r.hearing_count
            }
            for r in results
        ])
        
        # Calculate duration metrics
        df['case_age_days'] = df['filing_date'].apply(
            lambda x: calculate_case_age(x) if pd.notna(x) else None
        )
        
        # For disposed cases, calculate total duration
        df['total_duration_days'] = df.apply(  # type: ignore
            lambda row: (row['disposal_date'] - row['filing_date']).days 
            if pd.notna(row['disposal_date']) and pd.notna(row['filing_date'])
            else None,
            axis=1
        )
        
        # Calculate time to first hearing
        df['days_to_first_hearing'] = df.apply(  # type: ignore
            lambda row: (row['first_hearing_date'] - row['filing_date']).days
            if pd.notna(row['first_hearing_date']) and pd.notna(row['filing_date'])
            else None,
            axis=1
        )
        
        # Calculate average days between hearings
        df['avg_days_between_hearings'] = df.apply(  # type: ignore
            lambda row: row['case_age_days'] / row['hearing_count']
            if row['hearing_count'] > 0 and pd.notna(row['case_age_days'])
            else None,
            axis=1
        )
        
        logger.info(f"Analyzed {len(df)} cases")
        return df
        
    except Exception as e:
        logger.error(f"Error analyzing case durations: {str(e)}", exc_info=True)
        raise
    finally:
        if close_session:
            db_session.close()


def get_duration_statistics(
    duration_df: pd.DataFrame,
    group_by: str = 'case_type'
) -> pd.DataFrame:
    """
    Calculate summary statistics for case durations.
    
    Args:
        duration_df: DataFrame from analyze_case_durations
        group_by: Column to group by (case_type, court_code, state, etc.)
        
    Returns:
        DataFrame with statistical summaries
    """
    logger.info(f"Calculating duration statistics grouped by {group_by}")
    
    if duration_df.empty:
        logger.warning("Empty DataFrame provided")
        return pd.DataFrame()
    
    # Calculate statistics
    stats = duration_df.groupby(group_by).agg({
        'case_id': 'count',
        'case_age_days': ['mean', 'median', 'std', 'min', 'max'],
        'total_duration_days': ['mean', 'median', 'std', 'min', 'max'],
        'hearing_count': ['mean', 'median', 'max'],
        'days_to_first_hearing': ['mean', 'median'],
        'avg_days_between_hearings': ['mean', 'median']
    }).round(2)
    
    # Flatten column names
    stats.columns = ['_'.join(col).strip() for col in stats.columns.values]
    stats = stats.reset_index()
    
    # Rename for clarity
    stats.rename(columns={
        'case_id_count': 'total_cases'
    }, inplace=True)
    
    logger.info(f"Generated statistics for {len(stats)} groups")
    return stats


def identify_delayed_cases(
    duration_df: pd.DataFrame,
    threshold_days: int = 365,
    min_hearings: int = 5
) -> pd.DataFrame:
    """
    Identify cases that are significantly delayed.
    
    Args:
        duration_df: DataFrame from analyze_case_durations
        threshold_days: Minimum age in days to be considered delayed
        min_hearings: Minimum number of hearings for aged cases
        
    Returns:
        DataFrame of delayed cases with additional context
    """
    logger.info(f"Identifying delayed cases (>{threshold_days} days)")
    
    if duration_df.empty:
        return pd.DataFrame()
    
    # Filter delayed cases
    delayed = duration_df[
        (duration_df['case_age_days'] >= threshold_days) &
        (duration_df['case_status'].isin(['pending', 'adjourned']))
    ].copy()
    
    # Calculate delay severity score (higher = more urgent)
    delayed['delay_severity'] = (
        (delayed['case_age_days'] / 365) * 0.4 +  # Age factor
        (delayed['hearing_count'] / 10) * 0.3 +    # Hearing count factor
        (delayed['avg_days_between_hearings'] / 30) * 0.3  # Adjournment frequency
    ).round(2)
    
    # Sort by severity
    delayed = delayed.sort_values('delay_severity', ascending=False)
    
    logger.info(f"Found {len(delayed)} delayed cases")
    return delayed


def analyze_duration_trends(
    db_session: Optional[Session] = None,
    years: int = 3
) -> pd.DataFrame:
    """
    Analyze trends in case duration over time.
    
    Args:
        db_session: Database session
        years: Number of years to analyze
        
    Returns:
        DataFrame with monthly/yearly trends
    """
    logger.info(f"Analyzing duration trends for past {years} years")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=years * 365)
    
    df = analyze_case_durations(
        db_session=db_session,
        start_date=start_date,
        end_date=end_date
    )
    
    if df.empty:
        return pd.DataFrame()
    
    # Extract year and month
    df['filing_year'] = pd.to_datetime(df['filing_date']).dt.year
    df['filing_month'] = pd.to_datetime(df['filing_date']).dt.to_period('M')
    
    # Monthly trends
    monthly_trends = df.groupby('filing_month').agg({
        'case_id': 'count',
        'case_age_days': 'mean',
        'hearing_count': 'mean',
        'days_to_first_hearing': 'mean'
    }).round(2)
    
    monthly_trends.columns = [
        'cases_filed',
        'avg_case_age',
        'avg_hearings',
        'avg_days_to_first_hearing'
    ]
    
    logger.info(f"Generated trend data for {len(monthly_trends)} periods")
    return monthly_trends.reset_index()


def export_duration_analysis(
    duration_df: pd.DataFrame,
    output_path: str = "data/gold/case_duration_analysis.csv"
) -> None:
    """
    Export duration analysis results to CSV.
    
    Args:
        duration_df: DataFrame to export
        output_path: Path to save the CSV file
    """
    logger.info(f"Exporting duration analysis to {output_path}")
    
    try:
        duration_df.to_csv(output_path, index=False)
        logger.info(f"Successfully exported {len(duration_df)} records")
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    # Example usage
    logger.info("Running case duration analysis")
    
    # Analyze all cases
    df = analyze_case_durations()
    print(f"\nAnalyzed {len(df)} cases")
    print("\nFirst 5 rows:")
    print(df.head())
    
    # Get statistics by case type
    stats = get_duration_statistics(df, group_by='case_type')
    print("\nDuration Statistics by Case Type:")
    print(stats)
    
    # Identify delayed cases
    delayed = identify_delayed_cases(df, threshold_days=365)
    print(f"\nFound {len(delayed)} delayed cases")
    print("\nTop 5 most delayed cases:")
    print(delayed[['case_number', 'case_type', 'case_age_days', 'hearing_count', 'delay_severity']].head())
    
    # Export results
    export_duration_analysis(df)
