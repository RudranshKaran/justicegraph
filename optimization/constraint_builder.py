"""
Constraint Builder for Hearing Scheduling

Defines and validates constraints for the scheduling optimization engine.
"""

import pandas as pd
from datetime import date, datetime, timedelta
from typing import Dict, List, Tuple, Optional, Callable
import logging

from utils.logging_utils import get_logger

logger = get_logger(__name__)


class ConstraintBuilder:
    """
    Builder for scheduling constraints.
    """
    
    def __init__(self):
        """Initialize the constraint builder."""
        self.constraints = []
        logger.info("ConstraintBuilder initialized")
    
    def add_max_hearings_per_day(self, max_hearings: int) -> 'ConstraintBuilder':
        """
        Add constraint: Maximum hearings per day.
        
        Args:
            max_hearings: Maximum number of hearings allowed per day
            
        Returns:
            Self for chaining
        """
        constraint = {
            'type': 'max_hearings_per_day',
            'value': max_hearings,
            'description': f'No more than {max_hearings} hearings per day'
        }
        self.constraints.append(constraint)
        logger.info(f"Added constraint: {constraint['description']}")
        return self
    
    def add_max_hearings_per_judge(self, max_hearings: int) -> 'ConstraintBuilder':
        """
        Add constraint: Maximum hearings per judge per day.
        
        Args:
            max_hearings: Maximum hearings a judge can handle per day
            
        Returns:
            Self for chaining
        """
        constraint = {
            'type': 'max_hearings_per_judge',
            'value': max_hearings,
            'description': f'No judge can handle more than {max_hearings} hearings per day'
        }
        self.constraints.append(constraint)
        logger.info(f"Added constraint: {constraint['description']}")
        return self
    
    def add_priority_deadline(
        self,
        priority_threshold: float,
        max_days: int
    ) -> 'ConstraintBuilder':
        """
        Add constraint: High-priority cases must be scheduled within N days.
        
        Args:
            priority_threshold: Priority score threshold for urgent cases
            max_days: Maximum days before scheduling
            
        Returns:
            Self for chaining
        """
        constraint = {
            'type': 'priority_deadline',
            'priority_threshold': priority_threshold,
            'max_days': max_days,
            'description': f'Cases with priority >= {priority_threshold} must be scheduled within {max_days} days'
        }
        self.constraints.append(constraint)
        logger.info(f"Added constraint: {constraint['description']}")
        return self
    
    def add_minimum_gap_between_hearings(
        self,
        case_type: str,
        min_days: int
    ) -> 'ConstraintBuilder':
        """
        Add constraint: Minimum gap between consecutive hearings for a case.
        
        Args:
            case_type: Type of case this applies to
            min_days: Minimum days between hearings
            
        Returns:
            Self for chaining
        """
        constraint = {
            'type': 'minimum_gap',
            'case_type': case_type,
            'min_days': min_days,
            'description': f'{case_type} cases must have at least {min_days} days between hearings'
        }
        self.constraints.append(constraint)
        logger.info(f"Added constraint: {constraint['description']}")
        return self
    
    def add_working_hours_limit(
        self,
        max_hours: float,
        avg_hearing_duration: float
    ) -> 'ConstraintBuilder':
        """
        Add constraint: Total hearing time cannot exceed working hours.
        
        Args:
            max_hours: Maximum working hours per day
            avg_hearing_duration: Average duration per hearing in hours
            
        Returns:
            Self for chaining
        """
        max_hearings = int(max_hours / avg_hearing_duration)
        constraint = {
            'type': 'working_hours_limit',
            'max_hours': max_hours,
            'avg_duration': avg_hearing_duration,
            'max_hearings_derived': max_hearings,
            'description': f'Total hearing time cannot exceed {max_hours} hours per day (~{max_hearings} hearings)'
        }
        self.constraints.append(constraint)
        logger.info(f"Added constraint: {constraint['description']}")
        return self
    
    def add_judge_specialization(
        self,
        judge_id: int,
        case_types: List[str]
    ) -> 'ConstraintBuilder':
        """
        Add constraint: Judge can only handle specific case types.
        
        Args:
            judge_id: ID of the judge
            case_types: List of case types the judge can handle
            
        Returns:
            Self for chaining
        """
        constraint = {
            'type': 'judge_specialization',
            'judge_id': judge_id,
            'case_types': case_types,
            'description': f'Judge {judge_id} can only handle: {", ".join(case_types)}'
        }
        self.constraints.append(constraint)
        logger.info(f"Added constraint: {constraint['description']}")
        return self
    
    def add_no_weekend_scheduling(self) -> 'ConstraintBuilder':
        """
        Add constraint: No hearings on weekends.
        
        Returns:
            Self for chaining
        """
        constraint = {
            'type': 'no_weekends',
            'description': 'No hearings scheduled on weekends'
        }
        self.constraints.append(constraint)
        logger.info(f"Added constraint: {constraint['description']}")
        return self
    
    def add_holiday_exclusion(self, holidays: List[date]) -> 'ConstraintBuilder':
        """
        Add constraint: Exclude specific holiday dates.
        
        Args:
            holidays: List of holiday dates
            
        Returns:
            Self for chaining
        """
        constraint = {
            'type': 'holiday_exclusion',
            'holidays': holidays,
            'description': f'Exclude {len(holidays)} holidays from scheduling'
        }
        self.constraints.append(constraint)
        logger.info(f"Added constraint: {constraint['description']}")
        return self
    
    def add_balanced_workload(self, tolerance: float = 0.2) -> 'ConstraintBuilder':
        """
        Add constraint: Balance workload across judges.
        
        Args:
            tolerance: Allowable deviation from mean (e.g., 0.2 = 20%)
            
        Returns:
            Self for chaining
        """
        constraint = {
            'type': 'balanced_workload',
            'tolerance': tolerance,
            'description': f'Judge workload variance should not exceed {tolerance*100}%'
        }
        self.constraints.append(constraint)
        logger.info(f"Added constraint: {constraint['description']}")
        return self
    
    def get_constraints(self) -> List[Dict]:
        """
        Get all defined constraints.
        
        Returns:
            List of constraint dictionaries
        """
        return self.constraints
    
    def validate_schedule(
        self,
        schedule_df: pd.DataFrame,
        judges_df: pd.DataFrame
    ) -> Tuple[bool, List[str]]:
        """
        Validate a schedule against all constraints.
        
        Args:
            schedule_df: DataFrame with scheduled hearings
            judges_df: DataFrame with judge information
            
        Returns:
            Tuple of (is_valid, list of violations)
        """
        logger.info(f"Validating schedule with {len(self.constraints)} constraints")
        violations = []
        
        for constraint in self.constraints:
            constraint_type = constraint['type']
            
            if constraint_type == 'max_hearings_per_day':
                violations.extend(
                    self._validate_max_hearings_per_day(schedule_df, constraint)
                )
            
            elif constraint_type == 'max_hearings_per_judge':
                violations.extend(
                    self._validate_max_hearings_per_judge(schedule_df, constraint)
                )
            
            elif constraint_type == 'priority_deadline':
                violations.extend(
                    self._validate_priority_deadline(schedule_df, constraint)
                )
            
            elif constraint_type == 'no_weekends':
                violations.extend(
                    self._validate_no_weekends(schedule_df)
                )
            
            elif constraint_type == 'holiday_exclusion':
                violations.extend(
                    self._validate_holiday_exclusion(schedule_df, constraint)
                )
        
        is_valid = len(violations) == 0
        
        if is_valid:
            logger.info("✓ Schedule is valid - all constraints satisfied")
        else:
            logger.warning(f"✗ Schedule has {len(violations)} violations")
            for violation in violations:
                logger.warning(f"  - {violation}")
        
        return is_valid, violations
    
    def _validate_max_hearings_per_day(
        self,
        schedule_df: pd.DataFrame,
        constraint: Dict
    ) -> List[str]:
        """Validate maximum hearings per day constraint."""
        violations = []
        max_allowed = constraint['value']
        
        daily_counts = schedule_df.groupby('hearing_date').size()
        
        for hearing_date, count in daily_counts.items():
            if count > max_allowed:
                violations.append(
                    f"Date {hearing_date}: {count} hearings exceeds limit of {max_allowed}"
                )
        
        return violations
    
    def _validate_max_hearings_per_judge(
        self,
        schedule_df: pd.DataFrame,
        constraint: Dict
    ) -> List[str]:
        """Validate maximum hearings per judge per day constraint."""
        violations = []
        max_allowed = constraint['value']
        
        judge_daily_counts = schedule_df.groupby(['judge_id', 'hearing_date']).size()
        
        for key, count in judge_daily_counts.items():
            judge_id, hearing_date = key  # type: ignore
            if count > max_allowed:
                violations.append(
                    f"Judge {judge_id} on {hearing_date}: {count} hearings exceeds limit of {max_allowed}"
                )
        
        return violations
    
    def _validate_priority_deadline(
        self,
        schedule_df: pd.DataFrame,
        constraint: Dict
    ) -> List[str]:
        """Validate priority deadline constraint."""
        violations = []
        threshold = constraint['priority_threshold']
        max_days = constraint['max_days']
        
        if 'priority_score' not in schedule_df.columns:
            return violations
        
        today = datetime.now().date()
        deadline = today + timedelta(days=max_days)
        
        high_priority = schedule_df[schedule_df['priority_score'] >= threshold]
        
        for _, row in high_priority.iterrows():
            if row['hearing_date'] > deadline:
                violations.append(
                    f"Case {row['case_number']}: Priority {row['priority_score']} "
                    f"scheduled beyond {max_days}-day deadline"
                )
        
        return violations
    
    def _validate_no_weekends(self, schedule_df: pd.DataFrame) -> List[str]:
        """Validate no weekend scheduling constraint."""
        violations = []
        
        for _, row in schedule_df.iterrows():
            if row['hearing_date'].weekday() >= 5:  # Saturday=5, Sunday=6
                violations.append(
                    f"Case {row['case_number']} scheduled on weekend: {row['hearing_date']}"
                )
        
        return violations
    
    def _validate_holiday_exclusion(
        self,
        schedule_df: pd.DataFrame,
        constraint: Dict
    ) -> List[str]:
        """Validate holiday exclusion constraint."""
        violations = []
        holidays = constraint['holidays']
        
        for _, row in schedule_df.iterrows():
            if row['hearing_date'] in holidays:
                violations.append(
                    f"Case {row['case_number']} scheduled on holiday: {row['hearing_date']}"
                )
        
        return violations
    
    def export_constraints(self, output_path: str) -> None:
        """
        Export constraints to a readable format.
        
        Args:
            output_path: Path to save constraints
        """
        logger.info(f"Exporting {len(self.constraints)} constraints to {output_path}")
        
        with open(output_path, 'w') as f:
            f.write("# Scheduling Constraints\n\n")
            f.write(f"**Total Constraints:** {len(self.constraints)}\n\n")
            
            for i, constraint in enumerate(self.constraints, 1):
                f.write(f"{i}. **{constraint['type']}**: {constraint['description']}\n")
        
        logger.info(f"Constraints exported to {output_path}")


def create_default_constraints() -> ConstraintBuilder:
    """
    Create a constraint builder with standard judicial constraints.
    
    Returns:
        ConstraintBuilder with default constraints
    """
    builder = ConstraintBuilder()
    
    builder.add_max_hearings_per_day(20) \
           .add_max_hearings_per_judge(15) \
           .add_working_hours_limit(6.0, 0.5) \
           .add_priority_deadline(75.0, 7) \
           .add_no_weekend_scheduling() \
           .add_balanced_workload(0.25)
    
    logger.info("Created default constraint set")
    return builder


if __name__ == "__main__":
    # Example usage
    logger.info("Testing ConstraintBuilder")
    
    # Create constraints
    builder = create_default_constraints()
    
    # Add custom constraints
    builder.add_minimum_gap_between_hearings('criminal', 7)
    
    # Export
    builder.export_constraints("reports/SCHEDULING_CONSTRAINTS.md")
    
    print(f"\n✓ Created {len(builder.get_constraints())} constraints")
    print("\nConstraints:")
    for constraint in builder.get_constraints():
        print(f"  - {constraint['description']}")
