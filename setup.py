"""
JusticeGraph Setup Script

Run this script to set up the project for first-time use.
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def check_python_version():
    """Check if Python version is 3.9 or higher."""
    print_header("Checking Python Version")
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ ERROR: Python 3.9 or higher is required")
        return False
    
    print("✅ Python version is compatible")
    return True


def check_directories():
    """Check and create required directories."""
    print_header("Checking Directory Structure")
    
    required_dirs = [
        'data/bronze',
        'data/silver',
        'data/gold',
        'logs',
        'models',
        'ingest',
        'parse',
        'normalize',
        'pipelines',
        'validation',
        'utils',
        'configs',
        'documentation',
    ]
    
    for dir_path in required_dirs:
        full_path = PROJECT_ROOT / dir_path
        if full_path.exists():
            print(f"✅ {dir_path}")
        else:
            print(f"⚠️  Creating {dir_path}")
            full_path.mkdir(parents=True, exist_ok=True)
    
    return True


def check_config_files():
    """Check if configuration files exist."""
    print_header("Checking Configuration Files")
    
    # Check if settings.env exists
    settings_file = PROJECT_ROOT / 'configs' / 'settings.env'
    example_file = PROJECT_ROOT / 'configs' / 'settings.env.example'
    
    if not settings_file.exists():
        if example_file.exists():
            print("⚠️  settings.env not found")
            print(f"   Please copy {example_file.name} to settings.env")
            print(f"   and configure your database and other settings")
        else:
            print("❌ settings.env.example not found")
            return False
    else:
        print("✅ settings.env exists")
    
    # Check sources.yaml
    sources_file = PROJECT_ROOT / 'configs' / 'sources.yaml'
    if sources_file.exists():
        print("✅ sources.yaml exists")
    else:
        print("⚠️  sources.yaml not found")
    
    return True


def check_dependencies():
    """Check if required packages are installed."""
    print_header("Checking Dependencies")
    
    required_packages = [
        'sqlalchemy',
        'pandas',
        'requests',
        'beautifulsoup4',
        'pyyaml',
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NOT INSTALLED")
            missing_packages.append(package)
    
    if missing_packages:
        print("\n⚠️  Missing packages detected!")
        print("   Run: pip install -r requirements.txt")
        return False
    
    print("\n✅ All required dependencies are installed")
    return True


def initialize_database():
    """Initialize the database."""
    print_header("Database Initialization")
    
    try:
        from utils.db_utils import DatabaseManager
        
        print("Creating database manager...")
        db = DatabaseManager()
        
        print("Creating database tables...")
        db.create_tables()
        
        print("✅ Database initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        print("   Please check your DATABASE_URL in settings.env")
        return False


def run_tests():
    """Run the test suite."""
    print_header("Running Tests")
    
    response = input("Do you want to run the test suite? (y/n): ")
    
    if response.lower() == 'y':
        try:
            import test_pipeline
            success = test_pipeline.run_all_tests()
            return success
        except Exception as e:
            print(f"❌ Tests failed: {e}")
            return False
    else:
        print("⏭️  Skipping tests")
        return True


def print_next_steps():
    """Print next steps for the user."""
    print_header("Setup Complete! 🎉")
    
    print("""
Next Steps:

1. Configure your environment:
   - Edit configs/settings.env with your database credentials
   - Review configs/sources.yaml for data sources

2. Test the pipeline:
   - Run: python test_pipeline.py

3. Start collecting data:
   - Run: python pipelines/phase1_pipeline.py DL-HC 2023-11-01 2023-11-07

4. Explore the documentation:
   - README.md - Project overview
   - documentation/DATA_DICTIONARY.md - Data schema
   - documentation/PIPELINE_OVERVIEW.md - ETL workflow

5. Customize data sources:
   - Add scrapers in ingest/
   - Add parsers in parse/
   - Update configs/sources.yaml

For more information, visit:
https://github.com/RudranshKaran/justicegraph

Happy coding! 🚀
    """)


def main():
    """Main setup function."""
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║           JUSTICEGRAPH - PHASE 1 SETUP               ║
    ║        Data Collection & Preprocessing Pipeline      ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    
    checks = [
        ("Python Version", check_python_version),
        ("Directory Structure", check_directories),
        ("Configuration Files", check_config_files),
        ("Dependencies", check_dependencies),
    ]
    
    # Run all checks
    all_passed = True
    for check_name, check_func in checks:
        if not check_func():
            all_passed = False
    
    if not all_passed:
        print("\n⚠️  Some checks failed. Please resolve the issues above.")
        return False
    
    # Initialize database
    response = input("\nDo you want to initialize the database now? (y/n): ")
    if response.lower() == 'y':
        if not initialize_database():
            print("\n⚠️  Database initialization failed, but you can set it up later.")
    
    # Run tests (optional)
    # run_tests()  # Commented out by default
    
    # Print next steps
    print_next_steps()
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
