# -*- coding: utf-8 -*-
"""
JusticeGraph MVP - Complete Setup Script

Automates the entire MVP setup process:
1. Install dependencies
2. Generate sample data
3. Launch dashboard
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent


def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"▶ {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✓ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(e.stderr)
        return False


def check_python_version():
    """Check Python version."""
    print_header("Checking Python Version")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("✗ ERROR: Python 3.9 or higher required")
        return False
    
    print("✓ Python version compatible")
    return True


def install_dependencies():
    """Install required packages."""
    print_header("Installing Dependencies")
    
    requirements_file = PROJECT_ROOT / "requirements_mvp.txt"
    
    if not requirements_file.exists():
        print(f"✗ ERROR: {requirements_file} not found")
        return False
    
    print("Installing packages from requirements_mvp.txt...")
    print("This may take 2-3 minutes...\n")
    
    return run_command(
        f'pip install -r "{requirements_file}"',
        "Package installation"
    )


def generate_sample_data():
    """Generate sample CSV files."""
    print_header("Generating Sample Data")
    
    script_path = PROJECT_ROOT / "generate_sample_data.py"
    
    if not script_path.exists():
        print(f"✗ ERROR: {script_path} not found")
        return False
    
    return run_command(
        f'python "{script_path}"',
        "Sample data generation"
    )


def verify_setup():
    """Verify all required files exist."""
    print_header("Verifying Setup")
    
    required_files = [
        "frontend/app.py",
        "run_mvp.py",
        "data/gold/prioritized_cases.csv",
        "data/gold/optimized_schedule.csv",
        "data/gold/case_duration_analysis.csv"
    ]
    
    all_present = True
    for file in required_files:
        file_path = PROJECT_ROOT / file
        if file_path.exists():
            print(f"✓ {file}")
        else:
            print(f"✗ {file} - MISSING")
            all_present = False
    
    return all_present


def launch_dashboard():
    """Launch Streamlit dashboard."""
    print_header("Launching Dashboard")
    
    print("🚀 Starting Streamlit server...")
    print("📊 Dashboard will open in your browser")
    print("🔗 URL: http://localhost:8501")
    print("\n💡 Press Ctrl+C to stop the server\n")
    print("=" * 70 + "\n")
    
    app_path = PROJECT_ROOT / "frontend" / "app.py"
    
    try:
        subprocess.run(f'streamlit run "{app_path}"', shell=True, check=True)
    except KeyboardInterrupt:
        print("\n\n✓ Dashboard stopped")
    except Exception as e:
        print(f"\n✗ Error launching dashboard: {e}")


def main():
    """Main setup workflow."""
    print_header("JUSTICEGRAPH MVP - AUTOMATED SETUP")
    
    # Step 1: Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Step 2: Install dependencies
    print("\n⏳ This will install required packages. Continue? (y/n): ", end="")
    response = input().strip().lower()
    
    if response != 'y':
        print("Setup cancelled")
        sys.exit(0)
    
    if not install_dependencies():
        print("\n✗ Dependency installation failed")
        sys.exit(1)
    
    # Step 3: Generate sample data
    if not generate_sample_data():
        print("\n✗ Sample data generation failed")
        sys.exit(1)
    
    # Step 4: Verify setup
    if not verify_setup():
        print("\n⚠ WARNING: Some files are missing")
        print("Setup may be incomplete\n")
    
    # Step 5: Launch dashboard
    print_header("✅ SETUP COMPLETE")
    print("Ready to launch JusticeGraph MVP Dashboard!\n")
    print("Press Enter to start the dashboard (or Ctrl+C to exit)...")
    
    try:
        input()
        launch_dashboard()
    except KeyboardInterrupt:
        print("\n\nSetup complete. Run 'python run_mvp.py' to launch later.")


if __name__ == "__main__":
    main()
