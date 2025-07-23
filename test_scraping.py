#!/usr/bin/env python3
"""
Test script for the real scraping engine
"""

import asyncio
import json
import requests
import time

API_BASE_URL = "http://localhost:8000"

def test_authentication():
    """Test API authentication"""
    print("🔐 Testing authentication...")
    
    response = requests.post(f"{API_BASE_URL}/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Authentication successful")
        return token
    else:
        print(f"❌ Authentication failed: {response.text}")
        return None

def test_create_scraping_job(token, test_url="https://httpbin.org/html"):
    """Test creating a real scraping job"""
    print(f"🕷️ Creating scraping job for: {test_url}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    job_data = {
        "name": f"Test Scraping Job - {test_url}",
        "type": "web_scraping",
        "url": test_url,
        "scraper_type": "basic",
        "config": {
            "timeout": 30
        }
    }
    
    response = requests.post(f"{API_BASE_URL}/api/jobs", json=job_data, headers=headers)
    
    if response.status_code == 200:
        job_id = response.json()["id"]
        print(f"✅ Job created successfully with ID: {job_id}")
        return job_id
    else:
        print(f"❌ Job creation failed: {response.text}")
        return None

def test_start_job(token, job_id):
    """Test starting a scraping job"""
    print(f"▶️ Starting job {job_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(f"{API_BASE_URL}/api/jobs/{job_id}/start", headers=headers)
    
    if response.status_code == 200:
        print("✅ Job started successfully")
        return True
    else:
        print(f"❌ Job start failed: {response.text}")
        return False

def test_job_status(token, job_id, max_wait=30):
    """Monitor job status until completion"""
    print(f"👀 Monitoring job {job_id} status...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    start_time = time.time()
    while time.time() - start_time < max_wait:
        response = requests.get(f"{API_BASE_URL}/api/jobs/{job_id}", headers=headers)
        
        if response.status_code == 200:
            job = response.json()
            status = job["status"]
            print(f"📊 Job status: {status}")
            
            if status in ["completed", "failed"]:
                return job
            
        time.sleep(2)
    
    print("⏰ Timeout waiting for job completion")
    return None

def test_job_results(token, job_id):
    """Test getting job results"""
    print(f"📋 Getting results for job {job_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{API_BASE_URL}/api/jobs/{job_id}/results", headers=headers)
    
    if response.status_code == 200:
        results = response.json()
        print(f"✅ Retrieved {len(results)} results")
        
        # Print first result as sample
        if results:
            print("📄 Sample result:")
            print(json.dumps(results[0], indent=2)[:500] + "...")
        
        return results
    else:
        print(f"❌ Failed to get results: {response.text}")
        return None

def test_ecommerce_scraping(token):
    """Test e-commerce scraping"""
    print("🛒 Testing e-commerce scraping...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    job_data = {
        "name": "Test E-commerce Scraping",
        "type": "web_scraping",
        "url": "https://httpbin.org/html",  # Using test URL since real e-commerce sites may block
        "scraper_type": "e_commerce",
        "config": {}
    }
    
    response = requests.post(f"{API_BASE_URL}/api/jobs", json=job_data, headers=headers)
    
    if response.status_code == 200:
        job_id = response.json()["id"]
        print(f"✅ E-commerce job created: {job_id}")
        
        # Start and monitor the job
        if test_start_job(token, job_id):
            job = test_job_status(token, job_id)
            if job and job["status"] == "completed":
                test_job_results(token, job_id)
    else:
        print(f"❌ E-commerce job creation failed: {response.text}")

def test_api_scraping(token):
    """Test API scraping"""
    print("🔗 Testing API scraping...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    job_data = {
        "name": "Test API Scraping",
        "type": "api_scraping",
        "url": "https://httpbin.org/json",
        "scraper_type": "api",
        "config": {}
    }
    
    response = requests.post(f"{API_BASE_URL}/api/jobs", json=job_data, headers=headers)
    
    if response.status_code == 200:
        job_id = response.json()["id"]
        print(f"✅ API job created: {job_id}")
        
        # Start and monitor the job
        if test_start_job(token, job_id):
            job = test_job_status(token, job_id)
            if job and job["status"] == "completed":
                test_job_results(token, job_id)
    else:
        print(f"❌ API job creation failed: {response.text}")

def main():
    """Run all scraping tests"""
    print("🚀 Starting scraping engine tests...")
    print("=" * 50)
    
    # Test authentication
    token = test_authentication()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    print("\n" + "=" * 50)
    
    # Test basic web scraping
    job_id = test_create_scraping_job(token)
    if job_id:
        if test_start_job(token, job_id):
            job = test_job_status(token, job_id)
            if job and job["status"] == "completed":
                test_job_results(token, job_id)
    
    print("\n" + "=" * 50)
    
    # Test e-commerce scraping
    test_ecommerce_scraping(token)
    
    print("\n" + "=" * 50)
    
    # Test API scraping
    test_api_scraping(token)
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")

if __name__ == "__main__":
    main()
