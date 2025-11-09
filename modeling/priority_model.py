"""
Case Prioritization Model

Implements rule-based and ML-based approaches to assign urgency scores
to cases based on multiple factors including age, type, hearings, and workload.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
import pickle
import json

from models.data_models import Case, Court, Hearing, CaseType, CaseStatus
from utils.logging_utils import get_logger
from utils.db_utils import get_db_session

logger = get_logger(__name__)


class CasePrioritizer:
    """
    Case prioritization engine using rule-based scoring.
    
    Priority factors:
    - Case age (older = higher priority)
    - Case type (criminal > constitutional > civil)
    - Number of hearings/adjournments
    - Court workload
    - Special urgency factors
    """
    
    # Weight configuration for scoring
    WEIGHTS = {
        'age': 0.30,
        'case_type': 0.25,
        'hearing_count': 0.20,
        'court_workload': 0.15,
        'urgency_factors': 0.10
    }
    
    # Case type priority scores (higher = more urgent)
    CASE_TYPE_SCORES = {
        CaseType.CRIMINAL: 10,
        CaseType.WRIT: 9,
        CaseType.APPEAL: 7,
        CaseType.PETITION: 6,
        CaseType.CIVIL: 5,
        CaseType.REVISION: 5,
        CaseType.EXECUTION: 4,
        CaseType.MISC: 3
    }
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Initialize the prioritizer.
        
        Args:
            weights: Custom weight configuration (optional)
        """
        if weights:
            self.WEIGHTS = weights
        logger.info("CasePrioritizer initialized")
    
    def calculate_age_score(self, filing_date: datetime, max_age_days: int = 3650) -> float:
        """
        Calculate priority score based on case age.
        
        Args:
            filing_date: Date when case was filed
            max_age_days: Maximum age for normalization (default 10 years)
            
        Returns:
            Normalized score (0-10)
        """
        if filing_date is None:
            return 5.0  # Default middle score
        
        age_days = (datetime.now() - filing_date).days
        
        # Normalize to 0-10 scale
        score = min(10.0, (age_days / max_age_days) * 10)
        return round(score, 2)
    
    def calculate_case_type_score(self, case_type: Union[CaseType, str]) -> float:
        """
        Get priority score based on case type.
        
        Args:
            case_type: Type of the case
            
        Returns:
            Score (0-10)
        """
        if isinstance(case_type, str):
            try:
                case_type = CaseType(case_type.lower())
            except ValueError:
                return 5.0  # Default
        
        return float(self.CASE_TYPE_SCORES.get(case_type, 5))
    
    def calculate_hearing_score(self, hearing_count: int, max_hearings: int = 50) -> float:
        """
        Calculate score based on number of hearings/adjournments.
        
        Args:
            hearing_count: Number of hearings held
            max_hearings: Maximum hearings for normalization
            
        Returns:
            Score (0-10)
        """
        if hearing_count is None or hearing_count < 0:
            return 3.0
        
        # More hearings = more priority (case has been going on too long)
        score = min(10.0, (hearing_count / max_hearings) * 10)
        return round(score, 2)
    
    def calculate_workload_score(self, court_pending_cases: int, avg_pending: int = 500) -> float:
        """
        Calculate score based on court workload.
        
        Args:
            court_pending_cases: Number of pending cases at the court
            avg_pending: Average pending cases for normalization
            
        Returns:
            Score (0-10) - higher workload = higher priority
        """
        if court_pending_cases is None or court_pending_cases < 0:
            return 5.0
        
        # Inverse relationship: more workload = needs attention
        score = min(10.0, (court_pending_cases / avg_pending) * 10)
        return round(score, 2)
    
    def calculate_urgency_factors(
        self,
        case_data: Dict,
        special_keywords: Optional[List[str]] = None
    ) -> float:
        """
        Calculate additional urgency based on special factors.
        
        Args:
            case_data: Dictionary with case information
            special_keywords: Keywords indicating urgent cases
            
        Returns:
            Score (0-10)
        """
        if special_keywords is None:
            special_keywords = [
                'constitutional', 'habeas', 'bail', 'injunction',
                'interim', 'urgent', 'emergency', 'preventive detention'
            ]
        
        score = 0.0
        subject_matter = str(case_data.get('subject_matter', '')).lower()
        
        # Check for special keywords
        for keyword in special_keywords:
            if keyword in subject_matter:
                score += 2.0
        
        # Cap at 10
        return min(10.0, score)
    
    def calculate_priority_score(
        self,
        case_data: Dict,
        court_workload: Optional[int] = None
    ) -> float:
        """
        Calculate composite priority score for a case.
        
        Args:
            case_data: Dictionary with case information
            court_workload: Optional court workload data
            
        Returns:
            Priority score (0-100)
        """
        # Calculate individual component scores
        age_score = self.calculate_age_score(case_data.get('filing_date', datetime.now()))
        type_score = self.calculate_case_type_score(case_data.get('case_type', 'civil'))
        hearing_score = self.calculate_hearing_score(case_data.get('hearing_count', 0))
        workload_score = self.calculate_workload_score(court_workload or 500)
        urgency_score = self.calculate_urgency_factors(case_data)
        
        # Calculate weighted composite score
        composite = (
            age_score * self.WEIGHTS['age'] +
            type_score * self.WEIGHTS['case_type'] +
            hearing_score * self.WEIGHTS['hearing_count'] +
            workload_score * self.WEIGHTS['court_workload'] +
            urgency_score * self.WEIGHTS['urgency_factors']
        )
        
        # Normalize to 0-100 scale
        final_score = (composite / 10) * 100
        
        return round(final_score, 2)


def calculate_priority_scores(
    db_session: Optional[Session] = None,
    batch_size: int = 1000
) -> pd.DataFrame:
    """
    Calculate priority scores for all pending cases in the database.
    
    Args:
        db_session: Database session
        batch_size: Number of cases to process at once
        
    Returns:
        DataFrame with case IDs and priority scores
    """
    logger.info("Calculating priority scores for all pending cases")
    
    close_session = False
    if db_session is None:
        db_session = get_db_session()
        close_session = True
    
    try:
        # Initialize prioritizer
        prioritizer = CasePrioritizer()
        
        # Query pending cases with relevant data
        query = db_session.query(
            Case.case_id,
            Case.case_number,
            Case.case_type,
            Case.filing_date,
            Case.subject_matter,
            Court.court_id,
            Court.court_code,
            func.count(Hearing.hearing_id).label('hearing_count')
        ).join(Court, Case.court_id == Court.court_id
        ).outerjoin(Hearing, Case.case_id == Hearing.case_id
        ).filter(Case.is_pending == True
        ).group_by(
            Case.case_id,
            Case.case_number,
            Case.case_type,
            Case.filing_date,
            Case.subject_matter,
            Court.court_id,
            Court.court_code
        )
        
        results = query.all()
        
        if not results:
            logger.warning("No pending cases found")
            return pd.DataFrame()
        
        # Get court workload data
        court_workload = db_session.query(
            Court.court_id,
            func.count(Case.case_id).label('pending_count')
        ).join(Case, Court.court_id == Case.court_id
        ).filter(Case.is_pending == True
        ).group_by(Court.court_id
        ).all()
        
        workload_dict = {cw.court_id: cw.pending_count for cw in court_workload}
        
        # Calculate priority scores
        scores_data = []
        for result in results:
            case_data = {
                'filing_date': result.filing_date,
                'case_type': result.case_type,
                'subject_matter': result.subject_matter,
                'hearing_count': result.hearing_count
            }
            
            court_load = workload_dict.get(result.court_id, 500)
            priority_score = prioritizer.calculate_priority_score(case_data, court_load)
            
            scores_data.append({
                'case_id': result.case_id,
                'case_number': result.case_number,
                'case_type': result.case_type.value if result.case_type else None,
                'court_code': result.court_code,
                'filing_date': result.filing_date,
                'hearing_count': result.hearing_count,
                'priority_score': priority_score
            })
        
        # Convert to DataFrame
        df = pd.DataFrame(scores_data)
        
        # Add priority category
        df['priority_category'] = pd.cut(
            df['priority_score'],
            bins=[0, 33, 66, 100],
            labels=['Low', 'Medium', 'High']
        )
        
        # Sort by priority score
        df = df.sort_values('priority_score', ascending=False)
        
        logger.info(f"Calculated priority scores for {len(df)} cases")
        return df
        
    except Exception as e:
        logger.error(f"Error calculating priority scores: {str(e)}", exc_info=True)
        raise
    finally:
        if close_session:
            db_session.close()


def update_case_priorities_in_db(
    priority_df: pd.DataFrame,
    db_session: Optional[Session] = None
) -> int:
    """
    Update priority scores in the database.
    
    Args:
        priority_df: DataFrame with case_id and priority_score columns
        db_session: Database session
        
    Returns:
        Number of records updated
    """
    logger.info("Updating priority scores in database")
    
    close_session = False
    if db_session is None:
        db_session = get_db_session()
        close_session = True
    
    try:
        updated_count = 0
        
        for _, row in priority_df.iterrows():
            case = db_session.query(Case).filter(
                Case.case_id == row['case_id']
            ).first()
            
            if case:
                case.priority_score = row['priority_score']
                updated_count += 1
        
        db_session.commit()
        logger.info(f"Updated {updated_count} cases with priority scores")
        return updated_count
        
    except Exception as e:
        db_session.rollback()
        logger.error(f"Error updating priorities: {str(e)}", exc_info=True)
        raise
    finally:
        if close_session:
            db_session.close()


def export_prioritized_cases(
    priority_df: pd.DataFrame,
    output_path: str = "data/gold/prioritized_cases.csv"
) -> None:
    """
    Export prioritized cases to CSV.
    
    Args:
        priority_df: DataFrame with priority scores
        output_path: Output file path
    """
    logger.info(f"Exporting prioritized cases to {output_path}")
    
    try:
        priority_df.to_csv(output_path, index=False)
        logger.info(f"Exported {len(priority_df)} prioritized cases")
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}", exc_info=True)
        raise


def generate_priority_report(priority_df: pd.DataFrame) -> str:
    """
    Generate a summary report of prioritization results.
    
    Args:
        priority_df: DataFrame with priority scores
        
    Returns:
        Markdown-formatted report
    """
    report = []
    report.append("# Case Prioritization Report\n")
    report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append(f"**Total Cases Analyzed:** {len(priority_df)}\n\n")
    
    # Priority distribution
    report.append("## Priority Distribution\n")
    priority_counts = priority_df['priority_category'].value_counts()
    for category, count in priority_counts.items():
        percentage = (count / len(priority_df)) * 100
        report.append(f"- **{category}:** {count} ({percentage:.1f}%)\n")
    
    report.append("\n## Summary Statistics\n")
    report.append(f"- **Mean Priority Score:** {priority_df['priority_score'].mean():.2f}\n")
    report.append(f"- **Median Priority Score:** {priority_df['priority_score'].median():.2f}\n")
    report.append(f"- **Std Dev:** {priority_df['priority_score'].std():.2f}\n")
    
    # Top 10 high-priority cases
    report.append("\n## Top 10 High-Priority Cases\n")
    report.append("| Rank | Case Number | Court | Filing Date | Priority Score |\n")
    report.append("|------|-------------|-------|-------------|----------------|\n")
    
    for idx, row in priority_df.head(10).iterrows():
        rank = int(idx) + 1 if isinstance(idx, (int, float)) else 1  # type: ignore
        report.append(f"| {rank} | {row['case_number']} | {row['court_code']} | "
                     f"{row['filing_date'].strftime('%Y-%m-%d') if pd.notna(row['filing_date']) else 'N/A'} | "
                     f"{row['priority_score']:.2f} |\n")
    
    # Priority by case type
    report.append("\n## Priority by Case Type\n")
    type_priority = priority_df.groupby('case_type')['priority_score'].agg(['mean', 'count'])
    report.append("| Case Type | Avg Priority | Count |\n")
    report.append("|-----------|--------------|-------|\n")
    for case_type, stats in type_priority.iterrows():
        report.append(f"| {case_type} | {stats['mean']:.2f} | {int(stats['count'])} |\n")
    
    return ''.join(report)


if __name__ == "__main__":
    # Example usage
    logger.info("Running case prioritization")
    
    # Calculate priority scores
    priority_df = calculate_priority_scores()
    print(f"\nCalculated priorities for {len(priority_df)} cases")
    
    # Display statistics
    print("\nPriority Distribution:")
    print(priority_df['priority_category'].value_counts())
    
    print("\nTop 10 High-Priority Cases:")
    print(priority_df[['case_number', 'case_type', 'priority_score', 'priority_category']].head(10))
    
    # Export results
    export_prioritized_cases(priority_df)
    
    # Generate report
    report = generate_priority_report(priority_df)
    with open("reports/PRIORITY_METRICS.md", "w") as f:
        f.write(report)
    print("\n✓ Priority report saved to reports/PRIORITY_METRICS.md")
