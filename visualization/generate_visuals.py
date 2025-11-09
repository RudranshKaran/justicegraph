"""
Generate Visualizations for JusticeGraph Analytics

Creates charts, plots, and interactive visualizations for:
- Case distribution and backlogs
- Court performance metrics
- Priority distributions
- Judge workload analysis
- Trend analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
from pathlib import Path

from analysis.case_duration_analysis import analyze_case_durations, get_duration_statistics
from analysis.backlog_trends import analyze_backlog_trends, calculate_disposal_rate
from analysis.court_performance import analyze_court_performance, analyze_judge_workload
from utils.logging_utils import get_logger

logger = get_logger(__name__)

# Set visualization defaults
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")
COLORS = px.colors.qualitative.Set2


def ensure_output_dir(output_dir: str = "visualization/outputs") -> Path:
    """Ensure output directory exists."""
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def plot_case_distribution(
    cases_df: pd.DataFrame,
    output_dir: str = "visualization/outputs",
    show: bool = False
) -> None:
    """
    Create visualizations for case type and status distribution.
    
    Args:
        cases_df: DataFrame with case data
        output_dir: Directory to save plots
        show: Whether to display plots
    """
    logger.info("Generating case distribution plots")
    output_path = ensure_output_dir(output_dir)
    
    # 1. Case Type Distribution - Pie Chart
    if 'case_type' in cases_df.columns:
        fig = px.pie(
            cases_df,
            names='case_type',
            title='Case Distribution by Type',
            color_discrete_sequence=COLORS
        )
        fig.write_html(str(output_path / "case_type_distribution.html"))
        logger.info("Saved case type distribution")
    
    # 2. Case Status Distribution - Bar Chart
    if 'case_status' in cases_df.columns:
        status_counts = cases_df['case_status'].value_counts()
        
        fig = go.Figure(data=[
            go.Bar(
                x=status_counts.index,
                y=status_counts.values,
                marker_color=COLORS[0]
            )
        ])
        fig.update_layout(
            title='Case Distribution by Status',
            xaxis_title='Status',
            yaxis_title='Number of Cases'
        )
        fig.write_html(str(output_path / "case_status_distribution.html"))
        logger.info("Saved case status distribution")


def plot_backlog_trends(
    backlog_df: pd.DataFrame,
    output_dir: str = "visualization/outputs",
    show: bool = False
) -> None:
    """
    Visualize backlog trends and hotspots.
    
    Args:
        backlog_df: DataFrame from analyze_backlog_trends
        output_dir: Directory to save plots
        show: Whether to display plots
    """
    logger.info("Generating backlog trend visualizations")
    output_path = ensure_output_dir(output_dir)
    
    # Filter pending cases
    pending = backlog_df[backlog_df['case_status'] == 'pending'].copy()
    
    if pending.empty:
        logger.warning("No pending cases for visualization")
        return
    
    # 1. Top 10 Courts by Backlog - Horizontal Bar
    court_backlog = pending.groupby(['court_code', 'court_name'])['case_count'].sum()
    court_backlog = court_backlog.sort_values(ascending=False).head(10)
    
    fig = go.Figure(data=[
        go.Bar(
            y=court_backlog.index.get_level_values('court_name'),
            x=court_backlog.values,
            orientation='h',
            marker_color=COLORS[1]
        )
    ])
    fig.update_layout(
        title='Top 10 Courts by Pending Cases',
        xaxis_title='Number of Pending Cases',
        yaxis_title='Court',
        height=500
    )
    fig.write_html(str(output_path / "backlog_hotspots.html"))
    logger.info("Saved backlog hotspots")
    
    # 2. Backlog by Case Type
    type_backlog = pending.groupby('case_type')['case_count'].sum().sort_values(ascending=False)
    
    fig = px.bar(
        x=type_backlog.index,
        y=type_backlog.values,
        title='Pending Cases by Type',
        labels={'x': 'Case Type', 'y': 'Pending Cases'},
        color=type_backlog.values,
        color_continuous_scale='Reds'
    )
    fig.write_html(str(output_path / "backlog_by_type.html"))
    logger.info("Saved backlog by type")


def plot_judge_workload(
    workload_df: pd.DataFrame,
    output_dir: str = "visualization/outputs",
    show: bool = False
) -> None:
    """
    Visualize judge workload distribution.
    
    Args:
        workload_df: DataFrame from analyze_judge_workload
        output_dir: Directory to save plots
        show: Whether to display plots
    """
    logger.info("Generating judge workload visualizations")
    output_path = ensure_output_dir(output_dir)
    
    if workload_df.empty:
        logger.warning("No workload data for visualization")
        return
    
    # 1. Workload Distribution - Box Plot
    if 'unique_cases' in workload_df.columns:
        fig = go.Figure()
        fig.add_trace(go.Box(
            y=workload_df['unique_cases'],
            name='Cases per Judge',
            marker_color=COLORS[2]
        ))
        fig.update_layout(
            title='Judge Workload Distribution',
            yaxis_title='Number of Unique Cases'
        )
        fig.write_html(str(output_path / "judge_workload_distribution.html"))
        logger.info("Saved workload distribution")
    
    # 2. Top 10 Judges by Workload
    top_judges = workload_df.nlargest(10, 'unique_cases')
    
    fig = go.Figure(data=[
        go.Bar(
            x=top_judges['judge_name'],
            y=top_judges['unique_cases'],
            marker_color=COLORS[3]
        )
    ])
    fig.update_layout(
        title='Top 10 Judges by Workload',
        xaxis_title='Judge',
        yaxis_title='Unique Cases',
        xaxis_tickangle=-45
    )
    fig.write_html(str(output_path / "top_judges_workload.html"))
    logger.info("Saved top judges workload")


def plot_priority_distribution(
    priority_df: pd.DataFrame,
    output_dir: str = "visualization/outputs",
    show: bool = False
) -> None:
    """
    Visualize case priority distribution.
    
    Args:
        priority_df: DataFrame with priority scores
        output_dir: Directory to save plots
        show: Whether to display plots
    """
    logger.info("Generating priority distribution visualizations")
    output_path = ensure_output_dir(output_dir)
    
    if 'priority_score' not in priority_df.columns:
        logger.warning("No priority scores in DataFrame")
        return
    
    # 1. Priority Score Distribution - Histogram
    fig = go.Figure(data=[
        go.Histogram(
            x=priority_df['priority_score'],
            nbinsx=20,
            marker_color=COLORS[4]
        )
    ])
    fig.update_layout(
        title='Priority Score Distribution',
        xaxis_title='Priority Score',
        yaxis_title='Number of Cases'
    )
    fig.write_html(str(output_path / "priority_distribution.html"))
    logger.info("Saved priority distribution")
    
    # 2. Priority by Case Type - Box Plot
    if 'case_type' in priority_df.columns:
        fig = px.box(
            priority_df,
            x='case_type',
            y='priority_score',
            title='Priority Distribution by Case Type',
            color='case_type',
            color_discrete_sequence=COLORS
        )
        fig.update_xaxis(tickangle=-45)
        fig.write_html(str(output_path / "priority_by_case_type.html"))
        logger.info("Saved priority by case type")


def plot_duration_analysis(
    duration_df: pd.DataFrame,
    output_dir: str = "visualization/outputs",
    show: bool = False
) -> None:
    """
    Visualize case duration patterns.
    
    Args:
        duration_df: DataFrame from analyze_case_durations
        output_dir: Directory to save plots
        show: Whether to display plots
    """
    logger.info("Generating duration analysis visualizations")
    output_path = ensure_output_dir(output_dir)
    
    # 1. Duration Distribution by Case Type
    if 'case_age_days' in duration_df.columns and 'case_type' in duration_df.columns:
        fig = px.box(
            duration_df,
            x='case_type',
            y='case_age_days',
            title='Case Duration by Type',
            color='case_type',
            color_discrete_sequence=COLORS
        )
        fig.update_xaxis(tickangle=-45)
        fig.update_yaxis(title='Duration (days)')
        fig.write_html(str(output_path / "duration_by_type.html"))
        logger.info("Saved duration by type")
    
    # 2. Hearing Count vs Duration - Scatter
    if 'hearing_count' in duration_df.columns and 'case_age_days' in duration_df.columns:
        fig = px.scatter(
            duration_df,
            x='hearing_count',
            y='case_age_days',
            color='case_type' if 'case_type' in duration_df.columns else None,
            title='Hearing Count vs Case Duration',
            labels={'hearing_count': 'Number of Hearings', 'case_age_days': 'Case Age (days)'},
            opacity=0.6,
            color_discrete_sequence=COLORS
        )
        fig.write_html(str(output_path / "hearings_vs_duration.html"))
        logger.info("Saved hearings vs duration")


def plot_court_performance(
    performance_df: pd.DataFrame,
    output_dir: str = "visualization/outputs",
    show: bool = False
) -> None:
    """
    Visualize court performance metrics.
    
    Args:
        performance_df: DataFrame from analyze_court_performance
        output_dir: Directory to save plots
        show: Whether to display plots
    """
    logger.info("Generating court performance visualizations")
    output_path = ensure_output_dir(output_dir)
    
    # 1. Top 10 Courts by Performance Score
    if 'performance_score' in performance_df.columns:
        top_courts = performance_df.nlargest(10, 'performance_score')
        
        fig = go.Figure(data=[
            go.Bar(
                x=top_courts['court_name'],
                y=top_courts['performance_score'],
                marker_color=COLORS[5],
                text=top_courts['performance_score'].round(1),
                textposition='outside'
            )
        ])
        fig.update_layout(
            title='Top 10 Courts by Performance Score',
            xaxis_title='Court',
            yaxis_title='Performance Score',
            xaxis_tickangle=-45
        )
        fig.write_html(str(output_path / "top_performing_courts.html"))
        logger.info("Saved top performing courts")
    
    # 2. Disposal Rate vs Pending Cases - Scatter
    if all(col in performance_df.columns for col in ['disposal_rate', 'pending_cases']):
        fig = px.scatter(
            performance_df,
            x='pending_cases',
            y='disposal_rate',
            size='total_cases' if 'total_cases' in performance_df.columns else None,
            hover_name='court_name',
            title='Disposal Rate vs Pending Cases',
            labels={'pending_cases': 'Pending Cases', 'disposal_rate': 'Disposal Rate (%)'},
            color='disposal_rate',
            color_continuous_scale='RdYlGn'
        )
        fig.write_html(str(output_path / "disposal_vs_pending.html"))
        logger.info("Saved disposal vs pending")


def generate_all_visuals(output_dir: str = "visualization/outputs") -> None:
    """
    Generate all visualizations from current database state.
    
    Args:
        output_dir: Directory to save all plots
    """
    logger.info("Generating all visualizations")
    
    try:
        # Get data
        duration_df = analyze_case_durations()
        backlog_df = analyze_backlog_trends()
        performance_df = analyze_court_performance()
        workload_df = analyze_judge_workload()
        
        # Generate plots
        if not duration_df.empty:
            plot_duration_analysis(duration_df, output_dir)
        
        if not backlog_df.empty:
            plot_backlog_trends(backlog_df, output_dir)
        
        if not performance_df.empty:
            plot_court_performance(performance_df, output_dir)
        
        if not workload_df.empty:
            plot_judge_workload(workload_df, output_dir)
        
        logger.info(f"All visualizations saved to {output_dir}")
        print(f"\n✓ All visualizations generated in {output_dir}/")
        
    except Exception as e:
        logger.error(f"Error generating visualizations: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    # Generate all visualizations
    generate_all_visuals()
