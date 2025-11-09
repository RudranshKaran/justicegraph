"""
Visualization module for generating charts, plots, and dashboards.
"""

from .generate_visuals import (
    plot_case_distribution,
    plot_backlog_trends,
    plot_judge_workload,
    plot_priority_distribution
)
from .summary_dashboard import generate_summary_dashboard

__all__ = [
    'plot_case_distribution',
    'plot_backlog_trends',
    'plot_judge_workload',
    'plot_priority_distribution',
    'generate_summary_dashboard'
]
