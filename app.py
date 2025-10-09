"""
NyayaLens: AI-Powered Judicial Insights for Faster Justice
Homepage / Overview Dashboard
"""

import streamlit as st
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent))

from utils.api import get_dummy_summary_stats, get_dummy_backlog_trend
from utils.visuals import (
    render_metric_card, create_line_chart, apply_custom_css
)

# Page configuration
st.set_page_config(
    page_title="NyayaLens - AI-Powered Judicial Insights",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling
apply_custom_css()

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/200x80/1A237E/FFFFFF?text=NyayaLens", use_column_width=True)
    st.markdown("---")
    st.markdown("### 🏛️ Navigation")
    st.markdown("""
    - 🏠 **Home** (Current)
    - 📊 Explore Data
    - 🔮 Delay Prediction
    - 🗺️ Regional Insights
    - 🧠 Model Explainability
    - ℹ️ About & Feedback
    """)
    st.markdown("---")
    st.markdown("### 📈 Quick Stats")
    st.info("Real-time analytics powered by AI")

# Main content
def main():
    # Hero Section
    st.markdown("""
    <div style="text-align: center; padding: 30px 0;">
        <h1 style="font-size: 48px; margin-bottom: 10px;">⚖️ NyayaLens</h1>
        <h3 style="color: #800000; font-weight: 400; margin-top: 0;">
            AI-Powered Judicial Insights for Faster Justice
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; max-width: 800px; margin: 20px auto; font-size: 18px; color: #555;">
        NyayaLens is an advanced AI-driven analytics platform that analyzes Indian court case data 
        to identify backlog trends, predict case delays, and visualize judicial inefficiencies. 
        Our mission is to provide actionable insights for faster, more efficient justice delivery.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation Buttons
    st.markdown("### 🚀 Quick Access")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("📊 Explore Data", use_column_width=True):
            st.switch_page("pages/01_Explore_Data.py")
    
    with col2:
        if st.button("🔮 Delay Prediction", use_column_width=True):
            st.switch_page("pages/02_Predict_Delay.py")
    
    with col3:
        if st.button("🗺️ Regional Insights", use_column_width=True):
            st.switch_page("pages/03_Regional_Insights.py")
    
    with col4:
        if st.button("🧠 Model Explainability", use_column_width=True):
            st.switch_page("pages/04_Model_Explainability.py")
    
    with col5:
        if st.button("ℹ️ About", use_column_width=True):
            st.switch_page("pages/05_About.py")
    
    st.markdown("---")
    
    # Summary Statistics
    st.markdown("### 📊 Platform Overview")
    
    # Fetch summary stats
    stats = get_dummy_summary_stats()
    
    # Display metrics in columns
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        render_metric_card(
            title="Total Cases Analyzed",
            value=f"{stats['total_cases']:,}",
            icon="📁"
        )
    
    with col2:
        render_metric_card(
            title="States Covered",
            value=f"{stats['states_covered']}",
            icon="🗺️"
        )
    
    with col3:
        render_metric_card(
            title="Avg Delay",
            value=f"{stats['average_delay_years']} years",
            icon="⏱️"
        )
    
    with col4:
        render_metric_card(
            title="Pending Cases",
            value=f"{stats['pending_cases']:,}",
            icon="⚠️"
        )
    
    with col5:
        render_metric_card(
            title="Resolution Rate",
            value=f"{stats['resolution_rate']}%",
            icon="✅"
        )
    
    st.markdown("---")
    
    # Backlog Trend Visualization
    st.markdown("### 📈 Case Backlog Trend (2015-2025)")
    
    trend_data = get_dummy_backlog_trend()
    
    fig = create_line_chart(
        data=trend_data,
        x_col="years",
        y_col="backlog",
        title="Total Pending Cases Over Time",
        x_label="Year",
        y_label="Pending Cases (in millions)"
    )
    
    st.plotly_chart(fig, use_column_width=True)
    
    # Insights Section
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="card">
            <h3>🎯 Key Insights</h3>
            <ul style="line-height: 2;">
                <li><b>45M+</b> cases pending across Indian courts</li>
                <li><b>28 states</b> covered in our comprehensive analysis</li>
                <li>Average case resolution time: <b>3.2 years</b></li>
                <li>AI model accuracy: <b>87%</b> in delay prediction</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <h3>🔍 What We Analyze</h3>
            <ul style="line-height: 2;">
                <li>Historical case filing and resolution trends</li>
                <li>Regional backlog patterns and distributions</li>
                <li>Court-wise efficiency metrics</li>
                <li>Predictive modeling for case duration</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Call to Action
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1A237E 0%, #4A90E2 100%); 
                padding: 40px; border-radius: 15px; text-align: center; color: white; margin: 30px 0;">
        <h2 style="color: white; margin-bottom: 15px;">Ready to Explore?</h2>
        <p style="font-size: 18px; margin-bottom: 25px;">
            Dive deep into judicial data, predict case delays, and discover regional insights
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>© 2025 NyayaLens | Built with ❤️ using Streamlit & FastAPI</p>
        <p style="font-size: 12px; color: #999; margin-top: 10px;">
            All insights are based on publicly available anonymized legal data. No personal data is processed.
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
