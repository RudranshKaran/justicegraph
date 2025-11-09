# -*- coding: utf-8 -*-
"""
JusticeGraph MVP - Quick Launcher

Runs the Streamlit dashboard for demonstration.
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

def main():
    """Launch the Streamlit MVP dashboard."""
    
    print("\n" + "=" * 60)
    print("  JUSTICEGRAPH - MVP DASHBOARD")
    print("=" * 60 + "\n")
    
    print("🚀 Starting Streamlit server...")
    print("📊 Dashboard will open in your default browser")
    print("🔗 URL: http://localhost:8501")
    print("\n💡 Press Ctrl+C to stop the server\n")
    print("=" * 60 + "\n")
    
    # Change to project root directory
    os.chdir(PROJECT_ROOT)
    
    # Run Streamlit
    frontend_app = PROJECT_ROOT / "frontend" / "app.py"
    
    if not frontend_app.exists():
        print(f"❌ Error: {frontend_app} not found!")
        sys.exit(1)
    
    os.system(f"streamlit run {frontend_app}")


if __name__ == "__main__":
    main()
