"""
Hearing Scheduler - Optimization Engine

Implements intelligent hearing scheduling using constraint programming
and optimization algorithms to maximize court efficiency.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
from typing import Dict, List, Tuple, Optional
import logging
from sqlalchemy.orm import Session

# Import OR-Tools for optimization
try:
    from ortools.sat.python import cp_model
    ORTOOLS_AVAILABLE = True
except ImportError:
    ORTOOLS_AVAILABLE = False
    logging.warning("OR-Tools not available. Install with: pip install ortools")

from models.data_models import Case, Judge, Hearing, Court
from optimization.constraint_builder import ConstraintBuilder
from optimization.optimization_utils import validate_schedule, calculate_efficiency
from utils.logging_utils import get_logger
from utils.db_utils import get_db_session

logger = get_logger(__name__)


class HearingScheduler:
    """
    Optimized hearing scheduler using constraint programming.
    """
    
    def __init__(
        self,
        max_hearings_per_day: int = 20,
        max_hearings_per_judge: int = 15,
        working_hours_per_day: int = 6,
        avg_hearing_duration_hours: float = 0.5
    ):
        """
        Initialize the scheduler with constraints.
        
        Args:
            max_hearings_per_day: Maximum hearings court can handle per day
            max_hearings_per_judge: Maximum hearings per judge per day
            working_hours_per_day: Available hours per day
            avg_hearing_duration_hours: Average duration of a hearing
        """
        self.max_hearings_per_day = max_hearings_per_day
        self.max_hearings_per_judge = max_hearings_per_judge
        self.working_hours_per_day = working_hours_per_day
        self.avg_hearing_duration = avg_hearing_duration_hours
        
        if not ORTOOLS_AVAILABLE:
            logger.warning("OR-Tools not available. Using simple heuristic scheduling.")
        
        logger.info("HearingScheduler initialized")
    
    def schedule_hearings_heuristic(
        self,
        cases_df: pd.DataFrame,
        judges_df: pd.DataFrame,
        start_date: date,
        num_days: int = 30
    ) -> pd.DataFrame:
        """
        Generate hearing schedule using heuristic approach (no OR-Tools required).
        
        Args:
            cases_df: DataFrame with cases needing hearings
            judges_df: DataFrame with available judges
            start_date: Start date for scheduling
            num_days: Number of days to schedule
            
        Returns:
            DataFrame with scheduled hearings
        """
        logger.info(f"Generating heuristic schedule for {len(cases_df)} cases over {num_days} days")
        
        # Sort cases by priority (if priority_score exists)
        if 'priority_score' in cases_df.columns:
            cases_df = cases_df.sort_values('priority_score', ascending=False)
        
        schedule = []
        current_date = start_date
        
        # Initialize daily counters
        daily_hearings = {current_date + timedelta(days=i): 0 for i in range(num_days)}
        judge_daily_hearings = {
            (judge_id, current_date + timedelta(days=i)): 0
            for judge_id in judges_df['judge_id']
            for i in range(num_days)
        }
        
        # Schedule each case
        for idx, case_row in cases_df.iterrows():
            scheduled = False
            
            # Try to schedule on each day
            for day_offset in range(num_days):
                hearing_date = current_date + timedelta(days=day_offset)
                
                # Skip weekends (assuming Saturday=5, Sunday=6)
                if hearing_date.weekday() >= 5:
                    continue
                
                # Check daily capacity
                if daily_hearings[hearing_date] >= self.max_hearings_per_day:
                    continue
                
                # Try to assign to a judge
                for _, judge_row in judges_df.iterrows():
                    judge_id = judge_row['judge_id']
                    judge_key = (judge_id, hearing_date)
                    
                    # Check judge capacity
                    if judge_daily_hearings[judge_key] < self.max_hearings_per_judge:
                        # Schedule the hearing
                        schedule.append({
                            'case_id': case_row['case_id'],
                            'case_number': case_row['case_number'],
                            'judge_id': judge_id,
                            'judge_name': judge_row['judge_name'],
                            'hearing_date': hearing_date,
                            'priority_score': case_row.get('priority_score', 50),
                            'estimated_duration_hours': self.avg_hearing_duration
                        })
                        
                        # Update counters
                        daily_hearings[hearing_date] += 1
                        judge_daily_hearings[judge_key] += 1
                        scheduled = True
                        break
                
                if scheduled:
                    break
            
            if not scheduled:
                logger.warning(f"Could not schedule case {case_row['case_number']}")
        
        schedule_df = pd.DataFrame(schedule)
        logger.info(f"Scheduled {len(schedule_df)} hearings")
        
        return schedule_df
    
    def schedule_hearings_optimized(
        self,
        cases_df: pd.DataFrame,
        judges_df: pd.DataFrame,
        start_date: date,
        num_days: int = 30
    ) -> pd.DataFrame:
        """
        Generate optimized hearing schedule using OR-Tools CP-SAT solver.
        
        Args:
            cases_df: DataFrame with cases needing hearings
            judges_df: DataFrame with available judges
            start_date: Start date for scheduling
            num_days: Number of days to schedule
            
        Returns:
            DataFrame with optimized scheduled hearings
        """
        if not ORTOOLS_AVAILABLE:
            logger.warning("OR-Tools not available. Falling back to heuristic.")
            return self.schedule_hearings_heuristic(cases_df, judges_df, start_date, num_days)
        
        logger.info(f"Generating optimized schedule using OR-Tools for {len(cases_df)} cases")
        
        # Create CP-SAT model
        model = cp_model.CpModel()
        
        # Variables
        num_cases = len(cases_df)
        num_judges = len(judges_df)
        
        # Create scheduling variables
        # case_assignments[c][j][d] = 1 if case c is assigned to judge j on day d
        case_assignments = {}
        for c in range(num_cases):
            for j in range(num_judges):
                for d in range(num_days):
                    var_name = f'case_{c}_judge_{j}_day_{d}'
                    case_assignments[(c, j, d)] = model.NewBoolVar(var_name)
        
        # Constraint 1: Each case is scheduled exactly once
        for c in range(num_cases):
            model.Add(
                sum(case_assignments[(c, j, d)] 
                    for j in range(num_judges) 
                    for d in range(num_days)) == 1
            )
        
        # Constraint 2: Judge capacity per day
        for j in range(num_judges):
            for d in range(num_days):
                model.Add(
                    sum(case_assignments[(c, j, d)] for c in range(num_cases)) 
                    <= self.max_hearings_per_judge
                )
        
        # Constraint 3: Court capacity per day
        for d in range(num_days):
            model.Add(
                sum(case_assignments[(c, j, d)] 
                    for c in range(num_cases) 
                    for j in range(num_judges)) 
                <= self.max_hearings_per_day
            )
        
        # Objective: Maximize priority-weighted early scheduling
        objective_terms = []
        for c in range(num_cases):
            priority = cases_df.iloc[c].get('priority_score', 50)
            for j in range(num_judges):
                for d in range(num_days):
                    # Earlier days get higher weight
                    time_weight = num_days - d
                    objective_terms.append(
                        int(priority * time_weight) * case_assignments[(c, j, d)]
                    )
        
        model.Maximize(sum(objective_terms))
        
        # Solve
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 60.0
        status = solver.Solve(model)
        
        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            logger.info(f"Solution found with status: {solver.StatusName(status)}")
            
            # Extract schedule
            schedule = []
            for c in range(num_cases):
                for j in range(num_judges):
                    for d in range(num_days):
                        if solver.Value(case_assignments[(c, j, d)]) == 1:
                            hearing_date = start_date + timedelta(days=d)
                            
                            schedule.append({
                                'case_id': cases_df.iloc[c]['case_id'],
                                'case_number': cases_df.iloc[c]['case_number'],
                                'judge_id': judges_df.iloc[j]['judge_id'],
                                'judge_name': judges_df.iloc[j]['judge_name'],
                                'hearing_date': hearing_date,
                                'priority_score': cases_df.iloc[c].get('priority_score', 50),
                                'estimated_duration_hours': self.avg_hearing_duration
                            })
            
            schedule_df = pd.DataFrame(schedule)
            logger.info(f"Optimized schedule created with {len(schedule_df)} hearings")
            return schedule_df
        
        else:
            logger.error(f"No solution found. Status: {solver.StatusName(status)}")
            # Fall back to heuristic
            return self.schedule_hearings_heuristic(cases_df, judges_df, start_date, num_days)


def generate_optimal_schedule(
    court_code: Optional[str] = None,
    start_date: Optional[date] = None,
    num_days: int = 30,
    db_session: Optional[Session] = None,
    use_optimization: bool = True
) -> pd.DataFrame:
    """
    Generate optimal hearing schedule for a court.
    
    Args:
        court_code: Specific court to schedule (None for all courts)
        start_date: Start date for schedule (defaults to tomorrow)
        num_days: Number of days to schedule
        db_session: Database session
        use_optimization: Use OR-Tools optimization if available
        
    Returns:
        DataFrame with scheduled hearings
    """
    logger.info(f"Generating schedule for {court_code or 'all courts'}")
    
    close_session = False
    if db_session is None:
        db_session = get_db_session()
        close_session = True
    
    try:
        if start_date is None:
            start_date = (datetime.now() + timedelta(days=1)).date()
        
        # Get pending cases needing hearings
        query = db_session.query(
            Case.case_id,
            Case.case_number,
            Case.case_type,
            Case.priority_score,
            Court.court_id,
            Court.court_code
        ).join(Court, Case.court_id == Court.court_id
        ).filter(Case.is_pending == True)
        
        if court_code:
            query = query.filter(Court.court_code == court_code)
        
        cases = query.all()
        
        if not cases:
            logger.warning("No pending cases found")
            return pd.DataFrame()
        
        cases_df = pd.DataFrame([
            {
                'case_id': c.case_id,
                'case_number': c.case_number,
                'case_type': c.case_type.value if c.case_type else None,
                'priority_score': c.priority_score or 50,
                'court_id': c.court_id,
                'court_code': c.court_code
            }
            for c in cases
        ])
        
        # Get available judges
        judge_query = db_session.query(
            Judge.judge_id,
            Judge.judge_name,
            Judge.designation,
            Court.court_code
        ).join(Court, Judge.court_id == Court.court_id
        ).filter(Judge.is_active == True)
        
        if court_code:
            judge_query = judge_query.filter(Court.court_code == court_code)
        
        judges = judge_query.all()
        
        if not judges:
            logger.error("No active judges found")
            return pd.DataFrame()
        
        judges_df = pd.DataFrame([
            {
                'judge_id': j.judge_id,
                'judge_name': j.judge_name,
                'designation': j.designation,
                'court_code': j.court_code
            }
            for j in judges
        ])
        
        # Create scheduler
        scheduler = HearingScheduler()
        
        # Generate schedule
        if use_optimization and ORTOOLS_AVAILABLE:
            schedule_df = scheduler.schedule_hearings_optimized(
                cases_df, judges_df, start_date, num_days
            )
        else:
            schedule_df = scheduler.schedule_hearings_heuristic(
                cases_df, judges_df, start_date, num_days
            )
        
        return schedule_df
        
    except Exception as e:
        logger.error(f"Error generating schedule: {str(e)}", exc_info=True)
        raise
    finally:
        if close_session:
            db_session.close()


def export_schedule(
    schedule_df: pd.DataFrame,
    output_path: str = "data/gold/optimized_schedule.csv"
) -> None:
    """
    Export schedule to CSV.
    
    Args:
        schedule_df: DataFrame with schedule
        output_path: Output file path
    """
    logger.info(f"Exporting schedule to {output_path}")
    
    try:
        schedule_df.to_csv(output_path, index=False)
        logger.info(f"Exported {len(schedule_df)} scheduled hearings")
    except Exception as e:
        logger.error(f"Error exporting schedule: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    # Example usage
    logger.info("Running hearing scheduler")
    
    # Generate schedule
    schedule = generate_optimal_schedule(num_days=14)
    
    if not schedule.empty:
        print(f"\nGenerated schedule with {len(schedule)} hearings")
        print("\nSchedule summary:")
        print(schedule.groupby('hearing_date').size())
        
        # Export
        export_schedule(schedule)
        print("\n✓ Schedule exported to data/gold/optimized_schedule.csv")
