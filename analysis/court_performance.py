"""
Court Performance Analysis Module

Analyzes individual court performance metrics including:
- Case throughput and disposal efficiency
- Judge workload distribution
- Hearing frequency and patterns
- Court productivity rankings
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case as sql_case

from models.data_models import Case, Court, Judge, Hearing, CaseStatus
from utils.logging_utils import get_logger
from utils.db_utils import get_db_session

logger = get_logger(__name__)


def analyze_court_performance(
    db_session: Optional[Session] = None,
    time_period_months: int = 12
) -> pd.DataFrame:
    """
    Comprehensive court performance analysis.
    
    Args:
        db_session: Database session
        time_period_months: Analysis time window
        
    Returns:
        DataFrame with court performance metrics
    """
    logger.info(f"Analyzing court performance for past {time_period_months} months")
    
    close_session = False
    if db_session is None:
        db_session = get_db_session()
        close_session = True
    
    try:
        cutoff_date = datetime.now() - timedelta(days=time_period_months * 30)
        
        # Query court performance metrics
        query = db_session.query(
            Court.court_code,
            Court.court_name,
            Court.state,
            Court.court_type,
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
            ).label('pending_cases'),
            func.avg(
                func.extract('days', Case.disposal_date - Case.filing_date)
            ).label('avg_disposal_time_days'),
            func.count(func.distinct(Judge.judge_id)).label('judge_count')
        ).join(Court, Case.court_id == Court.court_id
        ).outerjoin(Hearing, Case.case_id == Hearing.case_id
        ).outerjoin(Judge, Hearing.judge_id == Judge.judge_id
        ).filter(Case.filing_date >= cutoff_date
        ).group_by(
            Court.court_code,
            Court.court_name,
            Court.state,
            Court.court_type
        )
        
        results = query.all()
        
        if not results:
            logger.warning("No court performance data found")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame([
            {
                'court_code': r.court_code,
                'court_name': r.court_name,
                'state': r.state,
                'court_type': r.court_type,
                'total_cases': r.total_cases,
                'disposed_cases': r.disposed_cases,
                'pending_cases': r.pending_cases,
                'disposal_rate': round((r.disposed_cases / r.total_cases * 100), 2) if r.total_cases > 0 else 0,
                'avg_disposal_time_days': round(float(r.avg_disposal_time_days), 2) if r.avg_disposal_time_days else None,
                'judge_count': r.judge_count,
                'cases_per_judge': round(r.total_cases / r.judge_count, 2) if r.judge_count > 0 else None
            }
            for r in results
        ])
        
        # Calculate performance score (0-100)
        df['performance_score'] = calculate_performance_score(df)
        
        logger.info(f"Analyzed performance for {len(df)} courts")
        return df
        
    except Exception as e:
        logger.error(f"Error analyzing court performance: {str(e)}", exc_info=True)
        raise
    finally:
        if close_session:
            db_session.close()


def calculate_performance_score(performance_df: pd.DataFrame) -> pd.Series:
    """
    Calculate a composite performance score for courts.
    
    Args:
        performance_df: DataFrame with performance metrics
        
    Returns:
        Series with performance scores (0-100)
    """
    # Normalize disposal rate (0-100)
    disposal_score = performance_df['disposal_rate']
    
    # Normalize disposal time (inverse - faster is better)
    if performance_df['avg_disposal_time_days'].notna().any():
        max_time = performance_df['avg_disposal_time_days'].max()
        time_score = (1 - (performance_df['avg_disposal_time_days'] / max_time)) * 100
        time_score = time_score.fillna(0)
    else:
        time_score = pd.Series([50] * len(performance_df))
    
    # Weighted composite score
    composite = (disposal_score * 0.6 + time_score * 0.4).round(2)
    
    return composite


def analyze_judge_workload(
    db_session: Optional[Session] = None,
    court_code: Optional[str] = None
) -> pd.DataFrame:
    """
    Analyze workload distribution across judges.
    
    Args:
        db_session: Database session
        court_code: Filter by specific court
        
    Returns:
        DataFrame with judge workload metrics
    """
    logger.info(f"Analyzing judge workload{' for ' + court_code if court_code else ''}")
    
    close_session = False
    if db_session is None:
        db_session = get_db_session()
        close_session = True
    
    try:
        # Query judge workload
        query = db_session.query(
            Judge.judge_id,
            Judge.judge_name,
            Judge.designation,
            Court.court_code,
            Court.court_name,
            func.count(func.distinct(Hearing.case_id)).label('unique_cases'),
            func.count(Hearing.hearing_id).label('total_hearings'),
            func.avg(
                func.extract('epoch', Hearing.hearing_date - Case.filing_date) / 86400
            ).label('avg_case_age_at_hearing')
        ).join(Court, Judge.court_id == Court.court_id
        ).join(Hearing, Judge.judge_id == Hearing.judge_id
        ).join(Case, Hearing.case_id == Case.case_id
        ).filter(Judge.is_active == True
        ).group_by(
            Judge.judge_id,
            Judge.judge_name,
            Judge.designation,
            Court.court_code,
            Court.court_name
        )
        
        if court_code:
            query = query.filter(Court.court_code == court_code)
        
        results = query.all()
        
        if not results:
            logger.warning("No judge workload data found")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame([
            {
                'judge_id': r.judge_id,
                'judge_name': r.judge_name,
                'designation': r.designation,
                'court_code': r.court_code,
                'court_name': r.court_name,
                'unique_cases': r.unique_cases,
                'total_hearings': r.total_hearings,
                'avg_hearings_per_case': round(r.total_hearings / r.unique_cases, 2) if r.unique_cases > 0 else 0,
                'avg_case_age_at_hearing': round(float(r.avg_case_age_at_hearing), 2) if r.avg_case_age_at_hearing else None
            }
            for r in results
        ])
        
        # Calculate workload intensity
        df['workload_intensity'] = (
            (df['unique_cases'] / df['unique_cases'].max()) * 0.5 +
            (df['total_hearings'] / df['total_hearings'].max()) * 0.5
        ).round(2)
        
        logger.info(f"Analyzed workload for {len(df)} judges")
        return df
        
    except Exception as e:
        logger.error(f"Error analyzing judge workload: {str(e)}", exc_info=True)
        raise
    finally:
        if close_session:
            db_session.close()


def rank_courts_by_efficiency(
    performance_df: pd.DataFrame,
    top_n: int = 10
) -> pd.DataFrame:
    """
    Rank courts by performance efficiency.
    
    Args:
        performance_df: DataFrame from analyze_court_performance
        top_n: Number of top courts to return
        
    Returns:
        DataFrame with ranked courts
    """
    logger.info(f"Ranking top {top_n} courts by efficiency")
    
    if performance_df.empty:
        return pd.DataFrame()
    
    # Sort by performance score
    ranked = performance_df.sort_values('performance_score', ascending=False).head(top_n)
    
    # Add rank column
    ranked['rank'] = range(1, len(ranked) + 1)
    
    logger.info(f"Generated rankings for top {len(ranked)} courts")
    return ranked


def identify_underperforming_courts(
    performance_df: pd.DataFrame,
    threshold_percentile: int = 25
) -> pd.DataFrame:
    """
    Identify courts that need intervention.
    
    Args:
        performance_df: DataFrame from analyze_court_performance
        threshold_percentile: Bottom percentile to flag
        
    Returns:
        DataFrame of underperforming courts
    """
    logger.info(f"Identifying courts below {threshold_percentile}th percentile")
    
    if performance_df.empty:
        return pd.DataFrame()
    
    # Calculate threshold
    threshold = performance_df['performance_score'].quantile(threshold_percentile / 100)
    
    # Filter underperforming courts
    underperforming = performance_df[
        performance_df['performance_score'] <= threshold
    ].copy()
    
    # Sort by performance score (worst first)
    underperforming = underperforming.sort_values('performance_score')
    
    logger.info(f"Identified {len(underperforming)} underperforming courts")
    return underperforming


def analyze_hearing_patterns(
    db_session: Optional[Session] = None,
    court_code: Optional[str] = None
) -> pd.DataFrame:
    """
    Analyze hearing scheduling patterns.
    
    Args:
        db_session: Database session
        court_code: Filter by specific court
        
    Returns:
        DataFrame with hearing pattern analysis
    """
    logger.info(f"Analyzing hearing patterns{' for ' + court_code if court_code else ''}")
    
    close_session = False
    if db_session is None:
        db_session = get_db_session()
        close_session = True
    
    try:
        # Query hearing patterns
        query = db_session.query(
            Court.court_code,
            func.extract('dow', Hearing.hearing_date).label('day_of_week'),
            func.count(Hearing.hearing_id).label('hearing_count'),
            func.count(func.distinct(Case.case_id)).label('unique_cases')
        ).join(Court, Case.court_id == Court.court_id
        ).join(Hearing, Case.case_id == Hearing.case_id
        ).group_by(
            Court.court_code,
            func.extract('dow', Hearing.hearing_date)
        )
        
        if court_code:
            query = query.filter(Court.court_code == court_code)
        
        results = query.all()
        
        if not results:
            logger.warning("No hearing pattern data found")
            return pd.DataFrame()
        
        # Convert to DataFrame
        day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        df = pd.DataFrame([
            {
                'court_code': r.court_code,
                'day_of_week': day_names[int(r.day_of_week)] if r.day_of_week is not None else None,
                'hearing_count': r.hearing_count,
                'unique_cases': r.unique_cases,
                'avg_hearings_per_case': round(r.hearing_count / r.unique_cases, 2) if r.unique_cases > 0 else 0
            }
            for r in results
        ])
        
        logger.info(f"Analyzed hearing patterns for {len(df)} court-day combinations")
        return df
        
    except Exception as e:
        logger.error(f"Error analyzing hearing patterns: {str(e)}", exc_info=True)
        raise
    finally:
        if close_session:
            db_session.close()


def export_performance_analysis(
    performance_df: pd.DataFrame,
    output_path: str = "data/gold/court_performance.csv"
) -> None:
    """
    Export court performance analysis to CSV.
    
    Args:
        performance_df: DataFrame to export
        output_path: Path to save the CSV file
    """
    logger.info(f"Exporting performance analysis to {output_path}")
    
    try:
        performance_df.to_csv(output_path, index=False)
        logger.info(f"Successfully exported {len(performance_df)} records")
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    # Example usage
    logger.info("Running court performance analysis")
    
    # Analyze court performance
    performance_df = analyze_court_performance(time_period_months=12)
    print(f"\nAnalyzed {len(performance_df)} courts")
    print("\nTop 5 performing courts:")
    print(performance_df.nlargest(5, 'performance_score'))
    
    # Analyze judge workload
    workload_df = analyze_judge_workload()
    print(f"\nAnalyzed workload for {len(workload_df)} judges")
    print("\nTop 5 judges by workload:")
    print(workload_df.nlargest(5, 'workload_intensity'))
    
    # Rank courts
    top_courts = rank_courts_by_efficiency(performance_df, top_n=10)
    print("\nTop 10 Courts by Efficiency:")
    print(top_courts[['rank', 'court_name', 'performance_score', 'disposal_rate']])
    
    # Identify underperforming courts
    underperforming = identify_underperforming_courts(performance_df)
    print(f"\nUnderperforming Courts: {len(underperforming)}")
    
    # Export results
    export_performance_analysis(performance_df)
