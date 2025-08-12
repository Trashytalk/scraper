#!/usr/bin/env python3
"""
Enhanced Test Runner for Business Intelligence Scraper
Fixes test collection issues and provides comprehensive test execution
"""

import sys
import os
import subprocess
import time
from pathlib import Path

def setup_environment():
    """Setup test environment and paths"""
    # Add project root to Python path
    project_root = Path(__file__).parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # Ensure all required directories exist
    test_dirs = ['tests', 'business_intel_scraper', 'security-reports']
    for dir_name in test_dirs:
        dir_path = project_root / dir_name
        if not dir_path.exists():
            dir_path.mkdir(exist_ok=True)

def run_command(command, description):
    """Run a command and return success status"""
    print(f"\n🔄 {description}")
    print("=" * 50)
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=False,
            text=True,
            cwd=Path(__file__).parent
        )
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED")
            return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def main():
    """Main test execution"""
    print("🧪 Enhanced Test Runner")
    print("Business Intelligence Scraper Platform")
    print("=" * 60)
    
    start_time = time.time()
    setup_environment()
    
    # Test categories to run
    tests = [
        # Basic validation
        ("python -m pytest tests/test_pytest_basic.py -v", "Basic Environment Tests"),
        
        # Specific working tests
        ("python -m pytest tests/test_advanced_crawling.py -v", "Advanced Crawling Tests"),
        ("python -m pytest tests/test_advanced_entity_graph.py -v", "Entity Graph Tests"),
        ("python -m pytest tests/test_data_models.py -v", "Data Models Tests"),
        
        # Core functionality
        ("python tests/api/test_api_quick.py", "Quick API Tests"),
        ("python validate_manual_testing.py", "Manual Testing Validation"),
        
        # Security tests (if available)
        ("./scripts/security-scan.sh", "Security Scanning"),
    ]
    
    passed = 0
    failed = 0
    
    for command, description in tests:
        if run_command(command, description):
            passed += 1
        else:
            failed += 1
    
    # Summary
    total_time = time.time() - start_time
    print(f"\n📊 Test Execution Summary")
    print("=" * 40)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⏱️ Total Time: {total_time:.2f}s")
    print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print(f"\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️ {failed} test categories failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
