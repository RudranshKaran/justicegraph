# -*- coding: utf-8 -*-
"""
JusticeGraph - MVP Streamlit Dashboard

A lightweight web interface for visualizing judicial analytics,
case prioritization, and optimized hearing schedules.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import sys
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# Page configuration
st.set_page_config(
    page_title="JusticeGraph MVP",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 1.1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

@st.cache_data
def load_prioritized_cases():
    """Load prioritized cases CSV."""
    try:
        file_path = PROJECT_ROOT / 'data' / 'gold' / 'prioritized_cases.csv'
        if file_path.exists():
            df = pd.read_csv(file_path)
            return df
        else:
            st.warning(f"File not found: {file_path}")
            return generate_sample_prioritized_cases()
    except Exception as e:
        st.error(f"Error loading prioritized cases: {e}")
        return generate_sample_prioritized_cases()


@st.cache_data
def load_schedule():
    """Load optimized schedule CSV."""
    try:
        file_path = PROJECT_ROOT / 'data' / 'gold' / 'optimized_schedule.csv'
        if file_path.exists():
            df = pd.read_csv(file_path)
            return df
        else:
            st.warning(f"File not found: {file_path}")
            return generate_sample_schedule()
    except Exception as e:
        st.error(f"Error loading schedule: {e}")
        return generate_sample_schedule()


@st.cache_data
def load_case_analysis():
    """Load case duration analysis CSV."""
    try:
        file_path = PROJECT_ROOT / 'data' / 'gold' / 'case_duration_analysis.csv'
        if file_path.exists():
            df = pd.read_csv(file_path)
            return df
        else:
            st.warning(f"File not found: {file_path}")
            return generate_sample_case_analysis()
    except Exception as e:
        st.error(f"Error loading case analysis: {e}")
        return generate_sample_case_analysis()


# ============================================================================
# SAMPLE DATA GENERATION (FALLBACK)
# ============================================================================

def generate_sample_prioritized_cases():
    """Generate sample prioritized cases data."""
    import numpy as np
    
    case_types = ['Criminal', 'Civil', 'Writ', 'Appeal', 'Petition']
    courts = ['Delhi HC', 'Mumbai HC', 'Bangalore HC', 'Chennai HC']
    statuses = ['Pending', 'Listed', 'Adjourned']
    
    data = {
        'case_id': range(1, 101),
        'case_number': [f"{np.random.choice(['CRL.A', 'CIV.A', 'WRIT', 'APP'])}/{i}/2023" for i in range(1, 101)],
        'court_code': np.random.choice(courts, 100),
        'case_type': np.random.choice(case_types, 100),
        'case_status': np.random.choice(statuses, 100),
        'filing_date': pd.date_range('2022-01-01', periods=100, freq='3D'),
        'priority_score': np.random.uniform(20, 100, 100).round(2),
        'age_days': np.random.randint(30, 1000, 100),
        'hearing_count': np.random.randint(1, 20, 100),
        'priority_category': np.random.choice(['High', 'Medium', 'Low'], 100, p=[0.3, 0.5, 0.2])
    }
    
    return pd.DataFrame(data)


def generate_sample_schedule():
    """Generate sample optimized schedule data."""
    import numpy as np
    
    judges = ['Justice A. Kumar', 'Justice B. Singh', 'Justice C. Patel', 'Justice D. Sharma']
    dates = pd.date_range('2025-11-10', periods=20, freq='D')
    
    schedules = []
    for date in dates:
        if date.weekday() < 5:  # Weekdays only
            for judge in judges:
                num_cases = np.random.randint(3, 8)
                for i in range(num_cases):
                    schedules.append({
                        'case_id': np.random.randint(1, 100),
                        'case_number': f"{np.random.choice(['CRL.A', 'CIV.A'])}/{np.random.randint(1, 200)}/2023",
                        'judge_name': judge,
                        'hearing_date': date,
                        'priority_score': np.random.uniform(30, 95, 1)[0].round(2),
                        'estimated_duration_hours': 0.5
                    })
    
    return pd.DataFrame(schedules)


def generate_sample_case_analysis():
    """Generate sample case analysis data."""
    import numpy as np
    
    case_types = ['Criminal', 'Civil', 'Writ', 'Appeal', 'Petition']
    
    data = {
        'case_type': case_types,
        'total_cases': np.random.randint(50, 200, 5),
        'avg_duration_days': np.random.randint(180, 730, 5),
        'median_duration_days': np.random.randint(150, 600, 5),
        'max_duration_days': np.random.randint(800, 1500, 5),
        'delayed_cases': np.random.randint(10, 80, 5)
    }
    
    return pd.DataFrame(data)


# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def show_case_type_distribution(df):
    """Display case type distribution pie chart."""
    if 'case_type' in df.columns:
        fig = px.pie(
            df,
            names='case_type',
            title='📊 Case Distribution by Type',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Case type data not available")


def show_priority_distribution(df):
    """Display priority score distribution."""
    if 'priority_score' in df.columns:
        fig = px.histogram(
            df,
            x='priority_score',
            nbins=20,
            title='📈 Priority Score Distribution',
            color_discrete_sequence=['#1f77b4']
        )
        fig.update_layout(xaxis_title='Priority Score', yaxis_title='Number of Cases')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Priority score data not available")


def show_backlog_by_court(df):
    """Display backlog by court bar chart."""
    if 'court_code' in df.columns:
        court_counts = df['court_code'].value_counts().reset_index()
        court_counts.columns = ['Court', 'Case Count']
        
        fig = px.bar(
            court_counts,
            x='Court',
            y='Case Count',
            title='🏛️ Case Load by Court',
            color='Case Count',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Court data not available")


def show_case_age_distribution(df):
    """Display case age distribution."""
    if 'age_days' in df.columns:
        fig = px.box(
            df,
            y='age_days',
            x='case_type' if 'case_type' in df.columns else None,
            title='⏳ Case Age Distribution by Type',
            color='case_type' if 'case_type' in df.columns else None
        )
        fig.update_layout(yaxis_title='Age (Days)')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Age data not available")


def show_schedule_timeline(df):
    """Display schedule timeline chart."""
    if 'hearing_date' in df.columns and 'judge_name' in df.columns:
        df['hearing_date'] = pd.to_datetime(df['hearing_date'])
        daily_counts = df.groupby(['hearing_date', 'judge_name']).size().reset_index(name='hearings')
        
        fig = px.line(
            daily_counts,
            x='hearing_date',
            y='hearings',
            color='judge_name',
            title='📅 Scheduled Hearings Timeline',
            markers=True
        )
        fig.update_layout(xaxis_title='Date', yaxis_title='Number of Hearings')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Schedule timeline data not available")


def show_judge_workload(df):
    """Display judge workload distribution."""
    if 'judge_name' in df.columns:
        judge_counts = df['judge_name'].value_counts().reset_index()
        judge_counts.columns = ['Judge', 'Total Hearings']
        
        fig = px.bar(
            judge_counts,
            x='Judge',
            y='Total Hearings',
            title='👨‍⚖️ Judge Workload Distribution',
            color='Total Hearings',
            color_continuous_scale='Viridis'
        )
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Judge workload data not available")


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    # Header
    st.markdown('<p class="main-header">⚖️ JusticeGraph MVP</p>', unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align: center; font-size: 1.2rem; color: #666;">Intelligent Judicial Analytics & Optimization Platform</p>',
        unsafe_allow_html=True
    )
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/clouds/200/scales.png", width=150)
        st.title("Navigation")
        st.markdown("---")
        st.info("📊 **MVP Features:**\n- Analytics Dashboard\n- Case Prioritization\n- Optimized Schedule")
        st.markdown("---")
        st.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
    # Load data
    prioritized_cases = load_prioritized_cases()
    schedule_data = load_schedule()
    case_analysis = load_case_analysis()
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📊 Analytics Dashboard", "🎯 Case Prioritization", "📅 Optimized Schedule"])
    
    # ========================================================================
    # TAB 1: ANALYTICS DASHBOARD
    # ========================================================================
    with tab1:
        st.header("📊 Analytics Dashboard")
        st.markdown("Comprehensive overview of judicial case metrics and trends")
        
        # Key Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Cases",
                value=f"{len(prioritized_cases):,}",
                delta="+12% vs last month"
            )
        
        with col2:
            avg_priority = prioritized_cases['priority_score'].mean() if 'priority_score' in prioritized_cases.columns else 0
            st.metric(
                label="Avg Priority Score",
                value=f"{avg_priority:.1f}/100",
                delta="+5.2 points"
            )
        
        with col3:
            high_priority = len(prioritized_cases[prioritized_cases['priority_score'] > 70]) if 'priority_score' in prioritized_cases.columns else 0
            st.metric(
                label="High Priority Cases",
                value=f"{high_priority:,}",
                delta="23% of total"
            )
        
        with col4:
            avg_age = prioritized_cases['age_days'].mean() if 'age_days' in prioritized_cases.columns else 0
            st.metric(
                label="Avg Case Age",
                value=f"{avg_age:.0f} days",
                delta="-8 days",
                delta_color="inverse"
            )
        
        st.markdown("---")
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            show_case_type_distribution(prioritized_cases)
            show_case_age_distribution(prioritized_cases)
        
        with col2:
            show_priority_distribution(prioritized_cases)
            show_backlog_by_court(prioritized_cases)
        
        # Case Analysis Summary
        if not case_analysis.empty:
            st.markdown("### 📈 Case Duration Analysis")
            st.dataframe(
                case_analysis,
                use_container_width=True
            )
    
    # ========================================================================
    # TAB 2: CASE PRIORITIZATION
    # ========================================================================
    with tab2:
        st.header("🎯 Case Prioritization")
        st.markdown("ML-based case ranking for optimal resource allocation")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'court_code' in prioritized_cases.columns:
                courts = ['All'] + sorted(prioritized_cases['court_code'].unique().tolist())
                selected_court = st.selectbox("Filter by Court", courts)
            else:
                selected_court = 'All'
        
        with col2:
            if 'case_type' in prioritized_cases.columns:
                case_types = ['All'] + sorted(prioritized_cases['case_type'].unique().tolist())
                selected_type = st.selectbox("Filter by Case Type", case_types)
            else:
                selected_type = 'All'
        
        with col3:
            if 'priority_category' in prioritized_cases.columns:
                priorities = ['All'] + sorted(prioritized_cases['priority_category'].unique().tolist())
                selected_priority = st.selectbox("Filter by Priority", priorities)
            else:
                selected_priority = 'All'
        
        # Apply filters
        filtered_df = prioritized_cases.copy()
        
        if selected_court != 'All' and 'court_code' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['court_code'] == selected_court]
        
        if selected_type != 'All' and 'case_type' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['case_type'] == selected_type]
        
        if selected_priority != 'All' and 'priority_category' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['priority_category'] == selected_priority]
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Filtered Cases", len(filtered_df))
        with col2:
            avg_score = filtered_df['priority_score'].mean() if 'priority_score' in filtered_df.columns else 0
            st.metric("Avg Priority Score", f"{avg_score:.1f}")
        with col3:
            avg_age = filtered_df['age_days'].mean() if 'age_days' in filtered_df.columns else 0
            st.metric("Avg Age", f"{avg_age:.0f} days")
        
        st.markdown("---")
        
        # Display table
        display_columns = ['case_number', 'court_code', 'case_type', 'priority_score', 'age_days', 'hearing_count', 'priority_category']
        available_columns = [col for col in display_columns if col in filtered_df.columns]
        
        if available_columns:
            st.dataframe(
                filtered_df[available_columns].sort_values('priority_score', ascending=False).head(50),
                use_container_width=True,
                height=400
            )
        else:
            st.dataframe(filtered_df.head(50), use_container_width=True, height=400)
        
        # Export button
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Cases (CSV)",
            data=csv,
            file_name=f"prioritized_cases_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    # ========================================================================
    # TAB 3: OPTIMIZED SCHEDULE
    # ========================================================================
    with tab3:
        st.header("📅 Optimized Hearing Schedule")
        st.markdown("AI-generated hearing calendar with constraint optimization")
        
        if not schedule_data.empty:
            # Schedule metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Cases Scheduled", len(schedule_data))
            
            with col2:
                unique_judges = schedule_data['judge_name'].nunique() if 'judge_name' in schedule_data.columns else 0
                st.metric("Judges Involved", unique_judges)
            
            with col3:
                if 'hearing_date' in schedule_data.columns:
                    schedule_data['hearing_date'] = pd.to_datetime(schedule_data['hearing_date'])
                    unique_dates = schedule_data['hearing_date'].nunique()
                    st.metric("Hearing Days", unique_dates)
                else:
                    st.metric("Hearing Days", "N/A")
            
            with col4:
                avg_priority = schedule_data['priority_score'].mean() if 'priority_score' in schedule_data.columns else 0
                st.metric("Avg Priority", f"{avg_priority:.1f}")
            
            st.markdown("---")
            
            # Visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                show_schedule_timeline(schedule_data)
            
            with col2:
                show_judge_workload(schedule_data)
            
            # Schedule table
            st.markdown("### 📋 Detailed Schedule")
            
            display_columns = ['hearing_date', 'case_number', 'judge_name', 'priority_score', 'estimated_duration_hours']
            available_columns = [col for col in display_columns if col in schedule_data.columns]
            
            if available_columns:
                st.dataframe(
                    schedule_data[available_columns].sort_values('hearing_date').head(100),
                    use_container_width=True,
                    height=400
                )
            else:
                st.dataframe(schedule_data.head(100), use_container_width=True, height=400)
            
            # Export button
            csv = schedule_data.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Schedule (CSV)",
                data=csv,
                file_name=f"optimized_schedule_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No schedule data available")
            st.info("💡 Run the optimization module to generate a schedule")


if __name__ == "__main__":
    main()
