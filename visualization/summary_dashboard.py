"""
Summary Dashboard Generator

Creates a comprehensive HTML dashboard combining all analytics and visualizations.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional
import logging

from analysis.case_duration_analysis import analyze_case_durations, get_duration_statistics
from analysis.backlog_trends import analyze_backlog_trends, calculate_disposal_rate
from analysis.court_performance import analyze_court_performance, analyze_judge_workload
from modeling.priority_model import calculate_priority_scores
from utils.logging_utils import get_logger

logger = get_logger(__name__)


def generate_summary_dashboard(
    output_path: str = "visualization/outputs/dashboard.html"
) -> None:
    """
    Generate a comprehensive summary dashboard with all key metrics and visualizations.
    
    Args:
        output_path: Path to save the HTML dashboard
    """
    logger.info("Generating summary dashboard")
    
    try:
        # Collect all data
        logger.info("Collecting data...")
        duration_df = analyze_case_durations()
        backlog_df = analyze_backlog_trends()
        performance_df = analyze_court_performance()
        workload_df = analyze_judge_workload()
        disposal_df = calculate_disposal_rate()
        
        # Calculate summary metrics
        total_cases = len(duration_df)
        pending_cases = len(duration_df[duration_df['case_status'] == 'pending'])
        disposed_cases = len(duration_df[duration_df['case_status'] == 'disposed'])
        avg_duration = duration_df['case_age_days'].mean() if not duration_df.empty else 0
        avg_hearings = duration_df['hearing_count'].mean() if not duration_df.empty else 0
        
        # Build HTML
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JusticeGraph Analytics Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .header .timestamp {{
            color: #666;
            font-size: 14px;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .metric-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
        }}
        
        .metric-label {{
            font-size: 14px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}
        
        .metric-value {{
            font-size: 36px;
            font-weight: bold;
            color: #667eea;
        }}
        
        .metric-subtitle {{
            font-size: 12px;
            color: #999;
            margin-top: 5px;
        }}
        
        .section {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .section h2 {{
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
        }}
        
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        .data-table th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        
        .data-table td {{
            padding: 10px 12px;
            border-bottom: 1px solid #f0f0f0;
        }}
        
        .data-table tr:hover {{
            background: #f9f9f9;
        }}
        
        .visualization-links {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        
        .viz-link {{
            display: block;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            text-align: center;
            transition: opacity 0.2s;
        }}
        
        .viz-link:hover {{
            opacity: 0.9;
        }}
        
        .footer {{
            text-align: center;
            color: white;
            margin-top: 30px;
            padding: 20px;
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }}
        
        .status-pending {{
            background: #fef3cd;
            color: #856404;
        }}
        
        .status-disposed {{
            background: #d4edda;
            color: #155724;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚖️ JusticeGraph Analytics Dashboard</h1>
            <p class="timestamp">Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Total Cases</div>
                <div class="metric-value">{total_cases:,}</div>
                <div class="metric-subtitle">Across all courts</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Pending Cases</div>
                <div class="metric-value">{pending_cases:,}</div>
                <div class="metric-subtitle">{(pending_cases/total_cases*100 if total_cases > 0 else 0):.1f}% of total</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Disposed Cases</div>
                <div class="metric-value">{disposed_cases:,}</div>
                <div class="metric-subtitle">{(disposed_cases/total_cases*100 if total_cases > 0 else 0):.1f}% of total</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Avg Duration</div>
                <div class="metric-value">{avg_duration:.0f}</div>
                <div class="metric-subtitle">Days per case</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Avg Hearings</div>
                <div class="metric-value">{avg_hearings:.1f}</div>
                <div class="metric-subtitle">Per case</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Courts Analyzed</div>
                <div class="metric-value">{len(performance_df)}</div>
                <div class="metric-subtitle">Active courts</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Interactive Visualizations</h2>
            <p>Click on any visualization below to explore detailed interactive charts:</p>
            <div class="visualization-links">
                <a href="case_type_distribution.html" class="viz-link">📈 Case Distribution</a>
                <a href="backlog_hotspots.html" class="viz-link">🔥 Backlog Hotspots</a>
                <a href="judge_workload_distribution.html" class="viz-link">⚖️ Judge Workload</a>
                <a href="priority_distribution.html" class="viz-link">🎯 Priority Distribution</a>
                <a href="duration_by_type.html" class="viz-link">⏱️ Duration Analysis</a>
                <a href="top_performing_courts.html" class="viz-link">🏆 Court Performance</a>
            </div>
        </div>
        
        <div class="section">
            <h2>🏛️ Top 10 Performing Courts</h2>
"""
        
        # Add top courts table
        if not performance_df.empty:
            top_courts = performance_df.nlargest(10, 'performance_score')
            html_content += """
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Court Name</th>
                        <th>Performance Score</th>
                        <th>Disposal Rate</th>
                        <th>Pending Cases</th>
                    </tr>
                </thead>
                <tbody>
"""
            for idx, row in enumerate(top_courts.itertuples(), 1):
                html_content += f"""
                    <tr>
                        <td>{idx}</td>
                        <td>{row.court_name if hasattr(row, 'court_name') else 'N/A'}</td>
                        <td>{row.performance_score if hasattr(row, 'performance_score') else 0:.2f}</td>
                        <td>{row.disposal_rate if hasattr(row, 'disposal_rate') else 0:.1f}%</td>
                        <td>{row.pending_cases if hasattr(row, 'pending_cases') else 0:,}</td>
                    </tr>
"""
            html_content += """
                </tbody>
            </table>
"""
        
        html_content += """
        </div>
        
        <div class="section">
            <h2>⚖️ Judge Workload Summary</h2>
"""
        
        # Add judge workload table
        if not workload_df.empty:
            top_judges = workload_df.nlargest(10, 'unique_cases')
            html_content += """
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Judge Name</th>
                        <th>Unique Cases</th>
                        <th>Total Hearings</th>
                        <th>Court</th>
                    </tr>
                </thead>
                <tbody>
"""
            for idx, row in enumerate(top_judges.itertuples(), 1):
                html_content += f"""
                    <tr>
                        <td>{idx}</td>
                        <td>{row.judge_name if hasattr(row, 'judge_name') else 'N/A'}</td>
                        <td>{row.unique_cases if hasattr(row, 'unique_cases') else 0}</td>
                        <td>{row.total_hearings if hasattr(row, 'total_hearings') else 0}</td>
                        <td>{row.court_code if hasattr(row, 'court_code') else 'N/A'}</td>
                    </tr>
"""
            html_content += """
                </tbody>
            </table>
"""
        
        html_content += f"""
        </div>
        
        <div class="section">
            <h2>📋 Case Duration Statistics</h2>
"""
        
        # Add duration statistics
        if not duration_df.empty:
            stats = get_duration_statistics(duration_df, group_by='case_type')
            if not stats.empty:
                html_content += """
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Case Type</th>
                        <th>Total Cases</th>
                        <th>Avg Duration (days)</th>
                        <th>Avg Hearings</th>
                    </tr>
                </thead>
                <tbody>
"""
                for row in stats.itertuples():
                    html_content += f"""
                    <tr>
                        <td>{row.case_type if hasattr(row, 'case_type') else 'N/A'}</td>
                        <td>{row.total_cases if hasattr(row, 'total_cases') else 0:,}</td>
                        <td>{row.case_age_days_mean if hasattr(row, 'case_age_days_mean') else 0:.0f}</td>
                        <td>{row.hearing_count_mean if hasattr(row, 'hearing_count_mean') else 0:.1f}</td>
                    </tr>
"""
                html_content += """
                </tbody>
            </table>
"""
        
        html_content += """
        </div>
        
        <div class="footer">
            <p>JusticeGraph Analytics Platform | Phase 2</p>
            <p>Powered by Python, Pandas, Plotly & SQLAlchemy</p>
        </div>
    </div>
</body>
</html>
"""
        
        # Save dashboard
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Dashboard saved to {output_path}")
        print(f"\n✓ Summary dashboard generated: {output_path}")
        
    except Exception as e:
        logger.error(f"Error generating dashboard: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    generate_summary_dashboard()
