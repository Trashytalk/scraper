#!/usr/bin/env python3
"""Test script to validate comprehensive error handling across the application."""

import json
import requests
import sys

BASE_URL = "http://localhost:8000"

def test_api_error_handling():
    """Test various error scenarios in the API."""
    print("🧪 Testing API Error Handling...")
    
    tests = [
        {
            "name": "Empty job name",
            "method": "POST",
            "url": f"{BASE_URL}/jobs/",
            "data": {"name": "", "url": "https://test.com", "scraper_type": "test"},
            "expected_status": 422,
            "expected_error": "Job name cannot be empty"
        },
        {
            "name": "Invalid URL format",
            "method": "POST", 
            "url": f"{BASE_URL}/jobs/",
            "data": {"name": "Test", "url": "invalid-url", "scraper_type": "test"},
            "expected_status": 422,
            "expected_error": "URL must start with http:// or https://"
        },
        {
            "name": "Invalid scraper type",
            "method": "POST",
            "url": f"{BASE_URL}/jobs/",
            "data": {"name": "Test", "url": "https://test.com", "scraper_type": "invalid"},
            "expected_status": 422,
            "expected_error": "Invalid scraper type"
        },
        {
            "name": "Non-existent job",
            "method": "GET",
            "url": f"{BASE_URL}/jobs/999",
            "expected_status": 404,
            "expected_error": "Job with ID 999 not found"
        },
        {
            "name": "Start non-existent job",
            "method": "POST",
            "url": f"{BASE_URL}/jobs/999/start",
            "expected_status": 404,
            "expected_error": "Job with ID 999 not found"
        },
        {
            "name": "Invalid job ID type",
            "method": "GET",
            "url": f"{BASE_URL}/jobs/abc",
            "expected_status": 422,
            "expected_error": "Input should be a valid integer"
        }
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test["method"] == "GET":
                response = requests.get(test["url"])
            elif test["method"] == "POST":
                response = requests.post(test["url"], json=test.get("data", {}))
            
            # Check status code
            if response.status_code == test["expected_status"]:
                # Check error message
                if response.status_code >= 400:
                    error_data = response.json()
                    detail = error_data.get("detail", "")
                    if isinstance(detail, list) and len(detail) > 0:
                        detail = detail[0].get("msg", "")
                    
                    if test["expected_error"] in str(detail):
                        print(f"✅ {test['name']}: PASSED")
                        passed += 1
                    else:
                        print(f"❌ {test['name']}: FAILED - Wrong error message: {detail}")
                        failed += 1
                else:
                    print(f"✅ {test['name']}: PASSED")
                    passed += 1
            else:
                print(f"❌ {test['name']}: FAILED - Expected status {test['expected_status']}, got {response.status_code}")
                failed += 1
                
        except Exception as e:
            print(f"❌ {test['name']}: FAILED - Exception: {e}")
            failed += 1
    
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    return failed == 0

def test_api_connectivity():
    """Test basic API connectivity."""
    print("🔗 Testing API Connectivity...")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ API server is running")
            return True
        else:
            print(f"❌ API server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API server: {e}")
        return False

def test_valid_operations():
    """Test valid operations work correctly."""
    print("✅ Testing Valid Operations...")
    
    try:
        # Test job creation
        job_data = {
            "name": "Test Error Handling Job",
            "url": "https://example.com",
            "scraper_type": "test",
            "schedule": "manual",
            "config": {}
        }
        
        response = requests.post(f"{BASE_URL}/jobs/", json=job_data)
        if response.status_code == 200:
            job = response.json()
            job_id = job["id"]
            print(f"✅ Job creation successful (ID: {job_id})")
            
            # Test job retrieval
            response = requests.get(f"{BASE_URL}/jobs/{job_id}")
            if response.status_code == 200:
                print("✅ Job retrieval successful")
            else:
                print(f"❌ Job retrieval failed: {response.status_code}")
                return False
            
            # Test job deletion
            response = requests.delete(f"{BASE_URL}/jobs/{job_id}")
            if response.status_code == 200:
                print("✅ Job deletion successful")
            else:
                print(f"❌ Job deletion failed: {response.status_code}")
                return False
            
            return True
        else:
            print(f"❌ Job creation failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Valid operations test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Comprehensive Error Handling Tests\n")
    
    all_passed = True
    
    # Test API connectivity first
    if not test_api_connectivity():
        print("❌ Cannot continue without API connectivity")
        sys.exit(1)
    
    print()
    
    # Test valid operations
    if not test_valid_operations():
        all_passed = False
    
    print()
    
    # Test error handling
    if not test_api_error_handling():
        all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 ALL TESTS PASSED - Error handling is comprehensive!")
        sys.exit(0)
    else:
        print("💥 SOME TESTS FAILED - Review error handling implementation")
        sys.exit(1)
