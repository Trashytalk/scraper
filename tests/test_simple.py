#!/usr/bin/env python3
"""
Simple Test to Verify Testing Environment

This is a basic test to ensure pytest and the testing environment are working.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_environment_setup():
    """Test that the environment is set up correctly"""
    print("🧪 Environment Setup Test")
    assert sys.version_info >= (3, 8), "Python 3.8+ required"
    assert project_root.exists(), "Project root should exist"
    print("✅ Environment setup test passed")

def test_basic_math():
    """Test basic math operations"""
    print("🔢 Basic Math Test")
    assert 2 + 2 == 4, "Basic addition should work"
    assert 5 * 3 == 15, "Basic multiplication should work"
    print("✅ Basic math test passed")

def test_file_system():
    """Test file system access"""
    print("📁 File System Test")
    assert os.path.exists('.'), "Current directory should exist"
    assert os.access('.', os.R_OK), "Should have read access to current directory"
    print("✅ File system test passed")

if __name__ == "__main__":
    test_environment_setup()
    test_basic_math()
    test_file_system()
    print("🎉 All basic tests passed!")
