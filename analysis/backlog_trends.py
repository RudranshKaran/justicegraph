"""
Backlog Trends Analysis Module

Analyzes court backlogs, pending case trends, and disposal rates
to identify systemic bottlenecks and capacity issues.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case as sql_case

from models.data_models import Case, Court, Hearing, CaseType, CaseStatus
from utils.logging_utils import get_logger
from utils.db_utils import get_db_session

logger = get_logger(__name__)


def analyze_backlog_trends(
    db_session: Optional[Session] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    group_by: str = 'court_code'
) -> pd.DataFrame:
    """
    Analyze backlog trends across courts and time periods.
    
    Args:
        db_session: Database session
        start_date: Start date for analysis
        end_date: End date for analysis
        group_by: Grouping dimension (court_code, state, case_type)
        
    Returns:
        DataFrame with backlog metrics
    """
    logger.info(f"Analyzing backlog trends grouped by {group_by}")
    
    close_session = False
    if db_session is None:
        db_session = get_db_session()
        close_session = True
    
    try:
        # Query for backlog analysis
        query = db_session.query(
            Court.court_code,
            Court.court_name,
            Court.state,
            Court.court_type,
            Case.case_type,
            Case.case_status,
            func.count(Case.case_id).label('case_count'),
            func.avg(
                func.extract('days', func.now() - Case.filing_date)
            ).label('avg_age_days'),
            func.min(Case.filing_date).label('oldest_case_date'),
            func.max(Case.filing_date).label('newest_case_date')
        ).join(Court, Case.court_id == Court.court_id
        ).group_by(
            Court.court_code,
            Court.court_name,
            Court.state,
            Court.court_type,
            Case.case_type,
            Case.case_status
        )
        
        # Apply date filters if provided
        if start_date:
            query = query.filter(Case.filing_date >= start_date)
        if end_date:
            query = query.filter(Case.filing_date <= end_date)
        
        results = query.all()
        
        if not results:
            logger.warning("No cases found for backlog analysis")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame([
            {
                'court_code': r.court_code,
                'court_name': r.court_name,
                'state': r.state,
                'court_type': r.court_type,
                'case_type': r.case_type.value if r.case_type else None,
                'case_status': r.case_status.value if r.case_status else None,
                'case_count': r.case_count,
                'avg_age_days': round(float(r.avg_age_days), 2) if r.avg_age_days else None,
                'oldest_case_date': r.oldest_case_date,
                'newest_case_date': r.newest_case_date
            }
            for r in results
        ])
        
        logger.info(f"Retrieved backlog data for {len(df)} court-case type combinations")
        return df
        
    except Exception as e:
        logger.error(f"Error analyzing backlog trends: {str(e)}", exc_info=True)
        raise
    finally:
        if close_session:
            db_session.close()


def calculate_disposal_rate(
    db_session: Optional[Session] = None,
    time_period_months: int = 12
) -> pd.DataFrame:
    """
    Calculate case disposal rates over a specified time period.
    
    Args:
        db_session: Database session
        time_period_months: Number of months to analyze
        
    Returns:
        DataFrame with disposal rate metrics by court
    """
    logger.info(f"Calculating disposal rates for past {time_period_months} months")
    
    close_session = False
    if db_session is None:
        db_session = get_db_session()
        close_session = True
    
    try:
        cutoff_date = datetime.now() - timedelta(days=time_period_months * 30)
        
        # Query for disposal statistics
        query = db_session.query(
            Court.court_code,
            Court.court_name,
            Court.state,
            func.count(Case.case_id).label('total_cases'),
            func.sum(
                sql_case(
                    (Case.case_status.in_([CaseStatus.DISPOSED, CaseStatus.DISMISSED, CaseStatus.DECREED]), 1),
                    else_=0
                )
            ).label('disposed_cases'),
            func.sum(
                sql_case(
                    (Case.case_status == CaseStatus.PENDING, 1),
                    else_=0
                )
            ).label('pending_cases')
        ).join(Court, Case.court_id == Court.court_id
        ).filter(Case.filing_date >= cutoff_date
        ).group_by(
            Court.court_code,
            Court.court_name,
            Court.state
        )
        
        results = query.all()
        
        if not results:
            logger.warning("No cases found for disposal rate calculation")
            return pd.DataFrame()
        
        # Convert to DataFrame and calculate rates
        df = pd.DataFrame([
            {
                'court_code': r.court_code,
                'court_name': r.court_name,
                'state': r.state,
                'total_cases': r.total_cases,
                'disposed_cases': r.disposed_cases,
                'pending_cases': r.pending_cases,
                'disposal_rate': round((r.disposed_cases / r.total_cases * 100), 2) if r.total_cases > 0 else 0,
                'pending_rate': round((r.pending_cases / r.total_cases * 100), 2) if r.total_cases > 0 else 0
            }
            for r in results
        ])
        
        # Sort by disposal rate
        df = df.sort_values('disposal_rate', ascending=False)
        
        logger.info(f"Calculated disposal rates for {len(df)} courts")
        return df
        
    except Exception as e:
        logger.error(f"Error calculating disposal rates: {str(e)}", exc_info=True)
        raise
    finally:
        if close_session:
            db_session.close()


def identify_backlog_hotspots(
    backlog_df: pd.DataFrame,
    threshold_percentile: float = 75
) -> pd.DataFrame:
    """
    Identify courts with severe backlogs.
    
    Args:
        backlog_df: DataFrame from analyze_backlog_trends
        threshold_percentile: Percentile threshold for identifying hotspots
        
    Returns:
        DataFrame of backlog hotspots
    """
    logger.info(f"Identifying backlog hotspots (>{threshold_percentile}th percentile)")
    
    if backlog_df.empty:
        return pd.DataFrame()
    
    # Filter for pending cases only
    pending = backlog_df[backlog_df['case_status'] == 'pending'].copy()
    
    # Group by court to get total pending cases
    court_backlog = pending.groupby(['court_code', 'court_name', 'state']).agg({
        'case_count': 'sum',
        'avg_age_days': 'mean'
    }).reset_index()
    
    # Calculate threshold
    threshold = court_backlog['case_count'].quantile(threshold_percentile / 100)
    
    # Identify hotspots
    hotspots = court_backlog[court_backlog['case_count'] >= threshold].copy()
    
    # Calculate severity score
    hotspots['backlog_severity'] = (
        (hotspots['case_count'] / hotspots['case_count'].max()) * 0.6 +
        (hotspots['avg_age_days'] / hotspots['avg_age_days'].max()) * 0.4
    ).round(2)
    
    # Sort by severity
    hotspots = hotspots.sort_values('backlog_severity', ascending=False)
    
    logger.info(f"Identified {len(hotspots)} backlog hotspots")
    return hotspots


def analyze_monthly_backlog_trend(
    db_session: Optional[Session] = None,
    months: int = 24
) -> pd.DataFrame:
    """
    Analyze how backlog has evolved month-over-month.
    
    Args:
        db_session: Database session
        months: Number of months to analyze
        
    Returns:
        DataFrame with monthly backlog trends
    """
    logger.info(f"Analyzing monthly backlog trends for past {months} months")
    
    close_session = False
    if db_session is None:
        db_session = get_db_session()
        close_session = True
    
    try:
        cutoff_date = datetime.now() - timedelta(days=months * 30)
        
        # Query cases filed in the period
        query = db_session.query(
            func.date_trunc('month', Case.filing_date).label('month'),
            func.count(Case.case_id).label('cases_filed'),
            func.sum(
                sql_case(
                    (Case.case_status.in_([CaseStatus.DISPOSED, CaseStatus.DISMISSED, CaseStatus.DECREED]), 1),
                    else_=0
                )
            ).label('cases_disposed')
        ).filter(
            Case.filing_date >= cutoff_date
        ).group_by(
            func.date_trunc('month', Case.filing_date)
        ).order_by(
            func.date_trunc('month', Case.filing_date)
        )
        
        results = query.all()
        
        if not results:
            logger.warning("No data found for monthly trend analysis")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame([
            {
                'month': r.month,
                'cases_filed': r.cases_filed,
                'cases_disposed': r.cases_disposed,
                'net_change': r.cases_filed - r.cases_disposed
            }
            for r in results
        ])
        
        # Calculate cumulative backlog change
        df['cumulative_backlog_change'] = df['net_change'].cumsum()
        
        logger.info(f"Generated monthly trends for {len(df)} months")
        return df
        
    except Exception as e:
        logger.error(f"Error analyzing monthly trends: {str(e)}", exc_info=True)
        raise
    finally:
        if close_session:
            db_session.close()


def compare_backlog_by_case_type(
    backlog_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Compare backlog severity across different case types.
    
    Args:
        backlog_df: DataFrame from analyze_backlog_trends
        
    Returns:
        DataFrame with case type comparison
    """
    logger.info("Comparing backlog by case type")
    
    if backlog_df.empty:
        return pd.DataFrame()
    
    # Filter pending cases
    pending = backlog_df[backlog_df['case_status'] == 'pending'].copy()
    
    # Group by case type
    comparison = pending.groupby('case_type').agg({
        'case_count': 'sum',
        'avg_age_days': 'mean'
    }).reset_index()
    
    # Calculate percentage
    comparison['percentage_of_backlog'] = (
        comparison['case_count'] / comparison['case_count'].sum() * 100
    ).round(2)
    
    # Sort by count
    comparison = comparison.sort_values('case_count', ascending=False)
    
    logger.info(f"Generated comparison for {len(comparison)} case types")
    return comparison


def export_backlog_analysis(
    backlog_df: pd.DataFrame,
    output_path: str = "data/gold/backlog_analysis.csv"
) -> None:
    """
    Export backlog analysis results to CSV.
    
    Args:
        backlog_df: DataFrame to export
        output_path: Path to save the CSV file
    """
    logger.info(f"Exporting backlog analysis to {output_path}")
    
    try:
        backlog_df.to_csv(output_path, index=False)
        logger.info(f"Successfully exported {len(backlog_df)} records")
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    # Example usage
    logger.info("Running backlog trends analysis")
    
    # Analyze backlog
    backlog_df = analyze_backlog_trends()
    print(f"\nAnalyzed backlog data: {len(backlog_df)} records")
    print("\nFirst 5 rows:")
    print(backlog_df.head())
    
    # Calculate disposal rates
    disposal_df = calculate_disposal_rate(time_period_months=12)
    print("\nDisposal Rates:")
    print(disposal_df.head())
    
    # Identify hotspots
    hotspots = identify_backlog_hotspots(backlog_df)
    print(f"\nBacklog Hotspots: {len(hotspots)} courts")
    print(hotspots.head())
    
    # Monthly trends
    monthly_trends = analyze_monthly_backlog_trend(months=12)
    print("\nMonthly Backlog Trends:")
    print(monthly_trends)
    
    # Export results
    export_backlog_analysis(backlog_df)
