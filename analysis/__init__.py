"""
Analysis module for exploratory data analysis and statistical summaries.
"""

from .case_duration_analysis import analyze_case_durations
from .backlog_trends import analyze_backlog_trends
from .court_performance import analyze_court_performance

__all__ = [
    'analyze_case_durations',
    'analyze_backlog_trends',
    'analyze_court_performance'
]
