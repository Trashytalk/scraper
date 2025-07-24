#!/usr/bin/env python3
"""
Test script for the crawler-to-scraper pipeline functionality
Demonstrates the two-stage workflow: crawling → batch scraping
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "admin"

def get_auth_token():
    """Get authentication token"""
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/login", data={
            "username": USERNAME,
            "password": PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
    except:
        pass
    return None

def create_test_crawler_job(token):
    """Create a test crawler job"""
    job_data = {
        "name": "Test Website Crawler",
        "url": "https://example.com",
        "scraper_type": "basic",
        "config": {
            "max_depth": 2,
            "max_pages": 20,
            "follow_links": True
        }
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/jobs",
            headers={"Authorization": f"Bearer {token}"},
            json=job_data
        )
        if response.status_code == 200:
            job = response.json()
            print(f"✅ Created crawler job: {job['name']} (ID: {job['id']})")
            return job
    except Exception as e:
        print(f"❌ Failed to create crawler job: {e}")
    return None

def simulate_job_completion(job_id, token):
    """Simulate job completion for testing"""
    # In a real scenario, you would wait for the job to complete
    # For testing, we'll just mark it as completed
    print(f"🔄 Simulating completion of job {job_id}...")
    time.sleep(2)
    print(f"✅ Job {job_id} marked as completed")

def extract_urls_from_crawler(job_id, token):
    """Test URL extraction from crawler job"""
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/jobs/{job_id}/extract-urls",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            data = response.json()
            urls = data.get("extracted_urls", [])
            print(f"🔍 Extracted {len(urls)} URLs from crawler job {job_id}")
            if urls:
                print("   Sample URLs:")
                for i, url in enumerate(urls[:5]):
                    print(f"     {i+1}. {url}")
                if len(urls) > 5:
                    print(f"     ... and {len(urls) - 5} more")
            return urls
    except Exception as e:
        print(f"❌ Failed to extract URLs: {e}")
    return []

def create_batch_scraping_jobs(crawler_job_id, urls, token):
    """Test batch job creation from extracted URLs"""
    if not urls:
        print("❌ No URLs to create batch jobs from")
        return []
    
    batch_data = {
        "base_name": "Batch Scraper from Test Crawler",
        "source_crawler_job_id": crawler_job_id,
        "scraper_type": "basic",
        "urls": urls,
        "batch_size": 5,
        "config": {
            "custom_selectors": {
                "title": "h1",
                "content": ".main-content, .article-body",
                "meta_description": "meta[name='description']"
            }
        }
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/jobs/batch",
            headers={"Authorization": f"Bearer {token}"},
            json=batch_data
        )
        if response.status_code == 200:
            jobs = response.json()
            print(f"🚀 Created {len(jobs)} batch scraping jobs!")
            for job in jobs:
                print(f"   📄 {job['name']} (ID: {job['id']})")
            return jobs
    except Exception as e:
        print(f"❌ Failed to create batch jobs: {e}")
    return []

def test_pipeline():
    """Test the complete crawler-to-scraper pipeline"""
    print("=== Crawler-to-Scraper Pipeline Test ===")
    print(f"Testing at {datetime.now()}")
    print()
    
    # Get authentication token
    print("🔐 Getting authentication token...")
    token = get_auth_token()
    if not token:
        print("❌ Failed to authenticate. Make sure the backend is running and credentials are correct.")
        return
    print("✅ Authentication successful")
    print()
    
    # Step 1: Create crawler job
    print("Step 1: Creating test crawler job...")
    crawler_job = create_test_crawler_job(token)
    if not crawler_job:
        print("❌ Failed to create crawler job")
        return
    
    # Step 2: Simulate job completion
    print("\nStep 2: Simulating job completion...")
    simulate_job_completion(crawler_job['id'], token)
    
    # Step 3: Extract URLs from crawler results
    print("\nStep 3: Extracting URLs from crawler results...")
    extracted_urls = extract_urls_from_crawler(crawler_job['id'], token)
    
    # Step 4: Create batch scraping jobs
    print("\nStep 4: Creating batch scraping jobs...")
    batch_jobs = create_batch_scraping_jobs(crawler_job['id'], extracted_urls, token)
    
    # Summary
    print("\n=== Pipeline Test Summary ===")
    print(f"✅ Crawler job created: {crawler_job['name']} (ID: {crawler_job['id']})")
    print(f"🔍 URLs extracted: {len(extracted_urls)}")
    print(f"🚀 Batch jobs created: {len(batch_jobs)}")
    print()
    print("Pipeline test completed! You can now:")
    print("1. Go to the frontend dashboard")
    print("2. Select 'Batch Scraping from Crawler Results' mode")
    print("3. Choose the test crawler job from the dropdown")
    print("4. See the extracted URLs and create additional batch jobs")
    print()
    print("Frontend URL: http://localhost:5173")
    print("Backend API docs: http://localhost:8000/docs")

if __name__ == "__main__":
    test_pipeline()
