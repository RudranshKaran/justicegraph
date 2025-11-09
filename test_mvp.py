"""
Test script to verify all MVP components work correctly.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))

def test_imports():
    """Test all required imports."""
    print("\n" + "=" * 60)
    print("Testing Imports")
    print("=" * 60)
    
    try:
        import streamlit
        print("✓ streamlit imported")
    except ImportError as e:
        print(f"✗ streamlit import failed: {e}")
        return False
    
    try:
        import plotly
        print("✓ plotly imported")
    except ImportError as e:
        print(f"✗ plotly import failed: {e}")
        return False
    
    try:
        import pandas
        print("✓ pandas imported")
    except ImportError as e:
        print(f"✗ pandas import failed: {e}")
        return False
    
    try:
        import numpy
        print("✓ numpy imported")
    except ImportError as e:
        print(f"✗ numpy import failed: {e}")
        return False
    
    return True


def test_data_files():
    """Test that all required data files exist."""
    print("\n" + "=" * 60)
    print("Testing Data Files")
    print("=" * 60)
    
    required_files = [
        'data/gold/prioritized_cases.csv',
        'data/gold/optimized_schedule.csv',
        'data/gold/case_duration_analysis.csv',
        'data/gold/backlog_trends.csv'
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = PROJECT_ROOT / file_path
        if full_path.exists():
            print(f"✓ {file_path} exists")
        else:
            print(f"✗ {file_path} NOT FOUND")
            all_exist = False
    
    return all_exist


def test_data_loading():
    """Test loading and validating data files."""
    print("\n" + "=" * 60)
    print("Testing Data Loading")
    print("=" * 60)
    
    import pandas as pd
    
    # Test prioritized cases
    try:
        df = pd.read_csv(PROJECT_ROOT / 'data/gold/prioritized_cases.csv')
        required_cols = ['case_id', 'case_number', 'court_code', 'case_type', 
                        'priority_score', 'age_days', 'hearing_count']
        
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            print(f"✗ prioritized_cases.csv missing columns: {missing}")
            return False
        
        print(f"✓ prioritized_cases.csv loaded: {len(df)} rows")
        print(f"  Columns: {df.columns.tolist()}")
    except Exception as e:
        print(f"✗ Failed to load prioritized_cases.csv: {e}")
        return False
    
    # Test schedule
    try:
        df = pd.read_csv(PROJECT_ROOT / 'data/gold/optimized_schedule.csv')
        required_cols = ['case_number', 'judge_name', 'hearing_date', 'priority_score']
        
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            print(f"✗ optimized_schedule.csv missing columns: {missing}")
            return False
        
        print(f"✓ optimized_schedule.csv loaded: {len(df)} rows")
        print(f"  Columns: {df.columns.tolist()}")
    except Exception as e:
        print(f"✗ Failed to load optimized_schedule.csv: {e}")
        return False
    
    # Test case analysis
    try:
        df = pd.read_csv(PROJECT_ROOT / 'data/gold/case_duration_analysis.csv')
        print(f"✓ case_duration_analysis.csv loaded: {len(df)} rows")
    except Exception as e:
        print(f"✗ Failed to load case_duration_analysis.csv: {e}")
        return False
    
    # Test backlog trends
    try:
        df = pd.read_csv(PROJECT_ROOT / 'data/gold/backlog_trends.csv')
        print(f"✓ backlog_trends.csv loaded: {len(df)} rows")
    except Exception as e:
        print(f"✗ Failed to load backlog_trends.csv: {e}")
        return False
    
    return True


def test_frontend_syntax():
    """Test frontend app for syntax errors."""
    print("\n" + "=" * 60)
    print("Testing Frontend Syntax")
    print("=" * 60)
    
    frontend_path = PROJECT_ROOT / 'frontend' / 'app.py'
    
    if not frontend_path.exists():
        print(f"✗ frontend/app.py NOT FOUND")
        return False
    
    try:
        with open(frontend_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        compile(code, str(frontend_path), 'exec')
        print(f"✓ frontend/app.py syntax valid")
        return True
    except SyntaxError as e:
        print(f"✗ Syntax error in frontend/app.py: {e}")
        return False
    except Exception as e:
        print(f"✗ Error checking frontend/app.py: {e}")
        return False


def test_launcher_scripts():
    """Test that launcher scripts exist."""
    print("\n" + "=" * 60)
    print("Testing Launcher Scripts")
    print("=" * 60)
    
    scripts = [
        'run_mvp.py',
        'setup_mvp.py',
        'generate_sample_data.py'
    ]
    
    all_exist = True
    for script in scripts:
        script_path = PROJECT_ROOT / script
        if script_path.exists():
            print(f"✓ {script} exists")
        else:
            print(f"✗ {script} NOT FOUND")
            all_exist = False
    
    return all_exist


def test_visualization_functions():
    """Test that visualization functions work with sample data."""
    print("\n" + "=" * 60)
    print("Testing Visualization Functions")
    print("=" * 60)
    
    try:
        import pandas as pd
        import plotly.express as px
        
        # Create sample data
        df = pd.DataFrame({
            'case_type': ['Criminal', 'Civil', 'Writ'],
            'count': [50, 30, 20]
        })
        
        # Test pie chart
        fig = px.pie(df, names='case_type', values='count')
        print("✓ Pie chart creation successful")
        
        # Test histogram
        df2 = pd.DataFrame({
            'priority_score': [45, 67, 89, 34, 78, 56, 91, 23]
        })
        fig = px.histogram(df2, x='priority_score')
        print("✓ Histogram creation successful")
        
        # Test bar chart
        fig = px.bar(df, x='case_type', y='count')
        print("✓ Bar chart creation successful")
        
        return True
    except Exception as e:
        print(f"✗ Visualization test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("  JUSTICEGRAPH MVP - COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Data Files", test_data_files),
        ("Data Loading", test_data_loading),
        ("Frontend Syntax", test_frontend_syntax),
        ("Launcher Scripts", test_launcher_scripts),
        ("Visualization Functions", test_visualization_functions)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("  TEST SUMMARY")
    print("=" * 60 + "\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:10} {test_name}")
    
    print("\n" + "=" * 60)
    print(f"  TOTAL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("=" * 60 + "\n")
    
    if passed == total:
        print("🎉 All tests passed! MVP is ready to run.")
        print("\nTo launch the dashboard:")
        print("  python run_mvp.py")
        return 0
    else:
        print("⚠️  Some tests failed. Please fix issues before running MVP.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
