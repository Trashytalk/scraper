#!/usr/bin/env python3
"""
Test script specifically for BBC Business URL batch job creation
"""

import requests
import json
import sys
from urllib.parse import urlparse

# Configuration
BASE_URL = "http://localhost:8000"
TEST_URL = "https://www.bbc.com/business"

def validate_url(url):
    """Validate that the URL is properly formatted"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def test_single_job_creation():
    """Test creating a single job first to isolate the issue"""
    print("🧪 Testing Single Job Creation with BBC Business")
    print("=" * 50)
    
    # Login first
    print("1. 🔐 Logging in...")
    login_data = {"username": "admin", "password": "admin123"}
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False
        
        token = response.json().get("access_token")
        print("✅ Login successful")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error during login: {e}")
        return False
    
    # Test single job creation
    print("2. 📊 Creating single job with BBC Business URL...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    single_job_data = {
        "name": "BBC Business Single Test",
        "type": "scraping",
        "url": TEST_URL,
        "scraper_type": "basic",
        "config": {
            "timeout": 30,
            "follow_redirects": True,
            "user_agent": "Business Intelligence Scraper"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/jobs", json=single_job_data, headers=headers)
        
        print(f"Single Job Response Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Single job created successfully: ID {result.get('id')}")
            return True
        else:
            print(f"❌ Single job creation failed: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error during single job creation: {e}")
        return False

def test_batch_job_with_bbc():
    """Test batch job creation specifically with BBC Business URL"""
    print("3. 📊 Testing Batch Job Creation with BBC Business")
    print("=" * 50)
    
    # Login first
    login_data = {"username": "admin", "password": "admin123"}
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        token = response.json().get("access_token")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error during login: {e}")
        return False
    
    # Test batch job creation with BBC URL
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    batch_data = {
        "base_name": "BBC Business Batch Test",
        "urls": [
            TEST_URL,
            "https://www.bbc.com/news/business",
            "https://www.bbc.com/news/business/companies"
        ],
        "scraper_type": "basic",
        "batch_size": 3,
        "config": {
            "timeout": 30,
            "follow_redirects": True,
            "user_agent": "Business Intelligence Scraper",
            "respect_robots": True
        }
    }
    
    print(f"📝 Batch data being sent:")
    print(json.dumps(batch_data, indent=2))
    
    try:
        response = requests.post(f"{BASE_URL}/api/jobs/batch", json=batch_data, headers=headers)
        
        print(f"Batch Job Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Batch job creation successful!")
            print(f"📊 Created {result.get('jobs_created', 0)} jobs")
            
            jobs = result.get('jobs', [])
            for i, job in enumerate(jobs, 1):
                print(f"  Job {i}: {job.get('name')} - {job.get('url')} - Status: {job.get('status')}")
            
            return True
        else:
            print(f"❌ Batch job creation failed: {response.status_code}")
            print(f"Error response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error during batch job creation: {e}")
        return False

def test_frontend_simulation():
    """Simulate how the frontend might be calling the API"""
    print("4. 🌐 Testing Frontend-like API Call")
    print("=" * 40)
    
    # Login first
    login_data = {"username": "admin", "password": "admin123"}
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        token = response.json().get("access_token")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error during login: {e}")
        return False
    
    # Simulate frontend fetch call
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "http://localhost:3000",  # Simulate frontend origin
        "Referer": "http://localhost:3000/"
    }
    
    # Simple batch data that frontend might send
    batch_data = {
        "base_name": "BBC Business Scraping",
        "urls": [TEST_URL],
        "scraper_type": "basic"
    }
    
    print(f"🧪 Simulating frontend fetch call...")
    print(f"Headers: {headers}")
    print(f"Data: {batch_data}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/jobs/batch", json=batch_data, headers=headers)
        
        print(f"Frontend Simulation Response Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Frontend simulation successful!")
            return True
        else:
            print(f"❌ Frontend simulation failed: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error in frontend simulation: {e}")
        print(f"This might be the source of your TypeError: NetworkError")
        return False

def check_cors_configuration():
    """Check CORS configuration"""
    print("5. 🔒 Checking CORS Configuration")
    print("=" * 35)
    
    try:
        response = requests.options(f"{BASE_URL}/api/jobs/batch", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type,Authorization"
        })
        
        print(f"CORS Preflight Status: {response.status_code}")
        print(f"CORS Headers: {dict(response.headers)}")
        
        if "access-control-allow-origin" in response.headers:
            print(f"✅ CORS Allow Origin: {response.headers['access-control-allow-origin']}")
        else:
            print("⚠️  No CORS Allow Origin header found")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ CORS check failed: {e}")

if __name__ == "__main__":
    print("🚀 BBC Business Batch Job Debugging")
    print("=" * 50)
    
    # Validate the test URL
    if not validate_url(TEST_URL):
        print(f"❌ Invalid test URL: {TEST_URL}")
        sys.exit(1)
    
    print(f"🎯 Testing with URL: {TEST_URL}")
    
    # Test server connectivity
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and accessible")
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Make sure the server is running with: ./quick_start.sh")
        sys.exit(1)
    
    # Run diagnostic tests
    print("\n" + "=" * 50)
    single_success = test_single_job_creation()
    print("\n" + "=" * 50)
    batch_success = test_batch_job_with_bbc()
    print("\n" + "=" * 50)
    frontend_success = test_frontend_simulation()
    print("\n" + "=" * 50)
    check_cors_configuration()
    
    print("\n" + "=" * 50)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    print(f"Single Job Creation: {'✅ PASS' if single_success else '❌ FAIL'}")
    print(f"Batch Job Creation: {'✅ PASS' if batch_success else '❌ FAIL'}")
    print(f"Frontend Simulation: {'✅ PASS' if frontend_success else '❌ FAIL'}")
    
    if not frontend_success:
        print("\n🔍 LIKELY ISSUE FOUND:")
        print("The NetworkError is probably a frontend/browser issue, not backend.")
        print("Possible causes:")
        print("1. CORS configuration issue")
        print("2. Frontend not using correct endpoint")
        print("3. Authentication token not properly sent")
        print("4. Frontend timeout settings")
    
    print("=" * 50)
