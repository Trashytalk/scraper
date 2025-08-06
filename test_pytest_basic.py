#!/usr/bin/env python3
"""
Basic Pytest Test to Verify Environment

This test ensures the pytest environment is working correctly.
"""

import pytest
import sys
import os
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

@pytest.mark.smoke
def test_pytest_working():
    """Test that pytest is working"""
    assert True, "Pytest should work"
    print("✅ Pytest is working correctly")

@pytest.mark.smoke  
def test_python_environment():
    """Test Python environment basics"""
    assert sys.version_info >= (3, 8), "Python 3.8+ required"
    assert PROJECT_ROOT.exists(), "Project root should exist"
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} environment OK")

@pytest.mark.unit
def test_basic_math():
    """Test basic arithmetic"""
    assert 2 + 2 == 4
    assert 10 / 2 == 5
    assert 3 * 4 == 12
    print("✅ Basic math operations working")

@pytest.mark.unit
def test_file_operations():
    """Test basic file operations"""
    assert os.path.exists(".")
    assert os.access(".", os.R_OK)
    print("✅ File system access working")

@pytest.mark.integration
def test_project_structure():
    """Test that key project files exist"""
    key_files = [
        "business_intel_scraper",
        "backend_server.py", 
        "scraping_engine.py",
        "requirements.txt"
    ]
    
    for file_path in key_files:
        assert Path(file_path).exists(), f"{file_path} should exist"
    
    print("✅ Project structure is correct")

@pytest.mark.integration
def test_import_core_modules():
    """Test importing core modules"""
    try:
        import business_intel_scraper
        print("✅ business_intel_scraper module imported")
    except ImportError as e:
        pytest.fail(f"Failed to import business_intel_scraper: {e}")
    
    try:
        import backend_server
        print("✅ backend_server module imported")
    except ImportError as e:
        pytest.fail(f"Failed to import backend_server: {e}")
    
    try:
        import scraping_engine  
        print("✅ scraping_engine module imported")
    except ImportError as e:
        pytest.fail(f"Failed to import scraping_engine: {e}")

if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v", "-s"])
