#!/usr/bin/env python3
"""
Quick Environment Test for Business Intelligence Scraper

This test checks if the basic environment is set up correctly
and can import the main modules.
"""

import sys
import os
from pathlib import Path

def test_python_environment():
    """Test the Python environment setup"""
    print("🐍 Python Environment Test")
    print("=" * 50)
    
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Current Working Directory: {os.getcwd()}")
    print(f"Python Path (first 5 entries):")
    for i, path in enumerate(sys.path[:5]):
        print(f"  {i+1}. {path}")
    
    print("\n📁 Project Structure Check:")
    project_root = Path.cwd()
    
    # Check for main directories
    key_dirs = [
        'business_intel_scraper',
        'tests',
        'backend_server.py',
        'scraping_engine.py'
    ]
    
    for item in key_dirs:
        path = project_root / item
        if path.exists():
            print(f"  ✅ {item} - Found")
        else:
            print(f"  ❌ {item} - Missing")
    
    print("\n🔧 Module Import Test:")
    
    # Add current directory to Python path
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
        print(f"  📝 Added {project_root} to Python path")
    
    # Test basic imports
    try:
        import business_intel_scraper
        print("  ✅ business_intel_scraper - Import successful")
    except ImportError as e:
        print(f"  ❌ business_intel_scraper - Import failed: {e}")
    
    try:
        from business_intel_scraper import backend
        print("  ✅ backend module - Import successful")
    except ImportError as e:
        print(f"  ❌ backend module - Import failed: {e}")
    
    try:
        import backend_server
        print("  ✅ backend_server - Import successful")
    except ImportError as e:
        print(f"  ❌ backend_server - Import failed: {e}")
    
    try:
        import scraping_engine
        print("  ✅ scraping_engine - Import successful")
    except ImportError as e:
        print(f"  ❌ scraping_engine - Import failed: {e}")
    
    print("\n🎯 Test Summary:")
    print("  Environment setup check completed!")

if __name__ == "__main__":
    test_python_environment()
