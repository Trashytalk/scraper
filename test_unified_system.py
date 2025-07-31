#!/usr/bin/env python3
"""
Test script for the unified web intelligence collection system
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5174"
TEST_USERNAME = "admin"
TEST_PASSWORD = "admin123"

def test_authentication():
    """Test login and get token"""
    print("🔐 Testing authentication...")
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    })
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        print("✅ Authentication successful")
        return token
    else:
        print(f"❌ Authentication failed: {response.status_code}")
        return None

def test_create_intelligent_crawling_job(token):
    """Test creating an intelligent crawling job"""
    print("\n🔗 Testing intelligent crawling job creation...")
    
    job_data = {
        "name": "Test Intelligent Crawling",
        "type": "intelligent_crawling",
        "url": "https://example.com",
        "scraper_type": "intelligent",
        "config": {
            "max_pages": 5,
            "max_depth": 2,
            "follow_internal_links": True,
            "follow_external_links": False,
            "rate_limit": {
                "requests_per_second": 1.0
            },
            "max_concurrent_workers": 3
        }
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/api/jobs", json=job_data, headers=headers)
    
    if response.status_code == 200:
        job_id = response.json().get("id")
        print(f"✅ Intelligent crawling job created with ID: {job_id}")
        return job_id
    else:
        print(f"❌ Job creation failed: {response.status_code} - {response.text}")
        return None

def test_create_single_page_job(token):
    """Test creating a single page extraction job"""
    print("\n📄 Testing single page extraction job creation...")
    
    job_data = {
        "name": "Test Single Page Extract",
        "type": "single_page",
        "url": "https://httpbin.org/html",
        "scraper_type": "basic",
        "config": {
            "timeout": 30,
            "retries": 2,
            "enable_js_rendering": False
        }
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/api/jobs", json=job_data, headers=headers)
    
    if response.status_code == 200:
        job_id = response.json().get("id")
        print(f"✅ Single page job created with ID: {job_id}")
        return job_id
    else:
        print(f"❌ Job creation failed: {response.status_code} - {response.text}")
        return None

def test_start_job(token, job_id, job_type):
    """Test starting a job"""
    print(f"\n▶️ Testing job execution for {job_type} (ID: {job_id})...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/api/jobs/{job_id}/start", headers=headers)
    
    if response.status_code == 200:
        print(f"✅ Job {job_id} started successfully")
        return True
    else:
        print(f"❌ Job start failed: {response.status_code} - {response.text}")
        return False

def test_job_status(token, job_id):
    """Test checking job status"""
    print(f"\n📊 Checking job status for ID: {job_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Wait for job to complete (max 30 seconds)
    for i in range(30):
        response = requests.get(f"{BASE_URL}/api/jobs/{job_id}", headers=headers)
        
        if response.status_code == 200:
            job_data = response.json()
            status = job_data.get("status")
            print(f"🔄 Job {job_id} status: {status}")
            
            if status == "completed":
                print(f"✅ Job {job_id} completed successfully")
                
                # Check if summary data is present
                config = job_data.get("config", {})
                summary = config.get("summary", {})
                if summary:
                    print(f"📊 Job Summary:")
                    print(f"   - Pages Processed: {summary.get('pages_processed', 0)}")
                    print(f"   - URLs Discovered: {summary.get('urls_discovered', 0)}")
                    print(f"   - URLs Queued: {summary.get('urls_queued', 0)}")
                    print(f"   - Data Extracted: {summary.get('data_extracted', 0)}")
                
                return True
            elif status == "failed":
                print(f"❌ Job {job_id} failed")
                return False
                
        time.sleep(1)
    
    print(f"⏰ Job {job_id} did not complete within 30 seconds")
    return False

def test_get_jobs(token):
    """Test getting job list with summary data"""
    print("\n📋 Testing job list retrieval...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/jobs", headers=headers)
    
    if response.status_code == 200:
        jobs = response.json()
        print(f"✅ Retrieved {len(jobs)} jobs")
        
        for job in jobs:
            print(f"📄 Job: {job.get('name')} (Type: {job.get('type')}, Status: {job.get('status')})")
            if hasattr(job, 'summary') or 'summary' in job:
                summary = job.get('summary', {})
                print(f"   📊 Summary: {summary}")
        
        return True
    else:
        print(f"❌ Failed to get jobs: {response.status_code}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Unified Web Intelligence Collection System")
    print("=" * 60)
    
    # Test authentication
    token = test_authentication()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    # Test job creation
    crawling_job_id = test_create_intelligent_crawling_job(token)
    single_page_job_id = test_create_single_page_job(token)
    
    # Test job execution for single page (faster to test)
    if single_page_job_id:
        if test_start_job(token, single_page_job_id, "single_page"):
            test_job_status(token, single_page_job_id)
    
    # Test getting jobs with summary data
    test_get_jobs(token)
    
    print("\n🎯 Test Results Summary:")
    print(f"   Frontend URL: {FRONTEND_URL}")
    print(f"   Backend URL: {BASE_URL}")
    print("   ✅ Ready for testing!")
    print("\n💡 Next Steps:")
    print("   1. Open the frontend URL to test the unified interface")
    print("   2. Create both types of collection jobs")
    print("   3. Verify inline results display and summaries")

if __name__ == "__main__":
    main()
