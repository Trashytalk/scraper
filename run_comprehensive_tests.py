#!/usr/bin/env python3
"""
Comprehensive Testing Runner for Business Intelligence Scraper

This script runs different categories of tests and provides a summary report.
"""

import subprocess
import sys
import time
import json
from datetime import datetime
from pathlib import Path

def run_command(cmd, timeout=60):
    """Run a command and capture output"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)

def test_category(name, command, description):
    """Run a test category and return results"""
    print(f"\n🧪 Running {name} Tests")
    print("=" * 50)
    print(f"Description: {description}")
    print(f"Command: {command}")
    print("-" * 50)
    
    start_time = time.time()
    returncode, stdout, stderr = run_command(command)
    end_time = time.time()
    duration = end_time - start_time
    
    success = returncode == 0
    
    result = {
        "name": name,
        "command": command,
        "success": success,
        "duration": duration,
        "returncode": returncode,
        "stdout": stdout,
        "stderr": stderr
    }
    
    if success:
        print(f"✅ {name} Tests PASSED (Duration: {duration:.2f}s)")
    else:
        print(f"❌ {name} Tests FAILED (Duration: {duration:.2f}s)")
        if stderr:
            print(f"Error: {stderr[:200]}...")
    
    # Show test summary from output
    if "passed" in stdout.lower() or "failed" in stdout.lower():
        lines = stdout.split('\n')
        for line in lines[-10:]:
            if 'passed' in line.lower() or 'failed' in line.lower() or 'error' in line.lower():
                print(f"  {line.strip()}")
    
    return result

def main():
    """Run comprehensive test suite"""
    print("🚀 BUSINESS INTELLIGENCE SCRAPER - COMPREHENSIVE TESTING")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.version}")
    print(f"Working Directory: {Path.cwd()}")
    
    # Activate virtual environment prefix (use bash explicitly)
    venv_prefix = "/bin/bash -c 'source .venv/bin/activate && "
    
    # Define test categories
    test_categories = [
        {
            "name": "Environment",
            "command": f"{venv_prefix}python test_pytest_basic.py'",
            "description": "Basic environment and setup validation"
        },
        {
            "name": "Smoke",
            "command": f"{venv_prefix}python -m pytest -m 'smoke' --tb=short -v'",
            "description": "Quick smoke tests for basic functionality"
        },
        {
            "name": "Unit",
            "command": f"{venv_prefix}python -m pytest -m 'unit' --tb=short -v'",
            "description": "Unit tests for individual components"
        },
        {
            "name": "API Basic",
            "command": f"{venv_prefix}python test_api_quick.py'",
            "description": "Basic API connectivity and endpoint tests"
        },
        {
            "name": "Import Tests",
            "command": f"{venv_prefix}python -c \"import business_intel_scraper; import backend_server; import scraping_engine; print('All imports successful')\"'",
            "description": "Test core module imports"
        }
    ]
    
    # Run test categories
    results = []
    total_duration = 0
    
    for category in test_categories:
        result = test_category(
            category["name"], 
            category["command"], 
            category["description"]
        )
        results.append(result)
        total_duration += result["duration"]
    
    # Summary report
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print("=" * 80)
    
    passed_tests = [r for r in results if r["success"]]
    failed_tests = [r for r in results if not r["success"]]
    
    print(f"✅ Passed: {len(passed_tests)}/{len(results)} test categories")
    print(f"❌ Failed: {len(failed_tests)}/{len(results)} test categories")
    print(f"⏱️ Total Duration: {total_duration:.2f} seconds")
    
    print(f"\n📈 Test Category Results:")
    for result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"  {status} {result['name']:15} ({result['duration']:.2f}s)")
    
    if failed_tests:
        print(f"\n⚠️ Failed Test Categories:")
        for result in failed_tests:
            print(f"  ❌ {result['name']}: {result['stderr'][:100] if result['stderr'] else 'Unknown error'}")
    
    # Overall assessment
    success_rate = len(passed_tests) / len(results) * 100
    print(f"\n🎯 Overall Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🏆 Testing Status: EXCELLENT - System is highly functional")
    elif success_rate >= 60:
        print("✅ Testing Status: GOOD - System is mostly functional")
    elif success_rate >= 40:
        print("⚠️ Testing Status: FAIR - System has some issues")
    else:
        print("❌ Testing Status: POOR - System needs attention")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return success_rate >= 60

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
