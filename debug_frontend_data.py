#!/usr/bin/env python3
"""
Debug script to test the frontend data display issue
"""

import requests
import json

def test_backend_data():
    # Login
    print("🔐 Testing backend authentication...")
    login_response = requests.post('http://localhost:8000/api/auth/login', 
                                   json={'username': 'admin', 'password': 'admin123'})
    
    if login_response.status_code != 200:
        print("❌ Login failed!")
        return
    
    token = login_response.json()['access_token']
    print("✅ Authentication successful")
    
    # Get jobs list
    print("\n📋 Testing jobs list...")
    jobs_response = requests.get('http://localhost:8000/api/jobs', 
                                headers={'Authorization': f'Bearer {token}'})
    
    if jobs_response.status_code != 200:
        print("❌ Jobs list failed!")
        return
    
    jobs = jobs_response.json()
    print(f"✅ Found {len(jobs)} jobs")
    
    if not jobs:
        print("⚠️ No jobs found to test")
        return
    
    # Test first completed job
    completed_jobs = [job for job in jobs if job['status'] == 'completed']
    if not completed_jobs:
        print("⚠️ No completed jobs found to test")
        return
    
    test_job = completed_jobs[0]
    job_id = test_job['id']
    print(f"\n🎯 Testing job {job_id}: {test_job['name']}")
    
    # Test job details
    print("\n📊 Testing job details...")
    details_response = requests.get(f'http://localhost:8000/api/jobs/{job_id}', 
                                   headers={'Authorization': f'Bearer {token}'})
    
    if details_response.status_code == 200:
        details = details_response.json()
        print("✅ Job details retrieved successfully")
        print(f"   - Name: {details.get('name', 'N/A')}")
        print(f"   - Status: {details.get('status', 'N/A')}")
        print(f"   - Type: {details.get('type', 'N/A')}")
        print(f"   - Config keys: {list(details.get('config', {}).keys())}")
    else:
        print("❌ Job details failed!")
    
    # Test job results
    print("\n📈 Testing job results...")
    results_response = requests.get(f'http://localhost:8000/api/jobs/{job_id}/results', 
                                   headers={'Authorization': f'Bearer {token}'})
    
    if results_response.status_code == 200:
        results_text = results_response.text
        print("✅ Job results retrieved successfully")
        print(f"   - Response size: {len(results_text)} characters")
        print(f"   - Content-Type: {results_response.headers.get('content-type', 'unknown')}")
        
        try:
            results_data = results_response.json()
            
            # Analyze the data structure
            if isinstance(results_data, list):
                print(f"   - Data type: List with {len(results_data)} items")
                if results_data:
                    first_item = results_data[0]
                    print(f"   - First item type: {type(first_item)}")
                    if isinstance(first_item, dict):
                        print(f"   - First item keys: {list(first_item.keys())}")
                        # Show a sample of the data
                        print("\n🔍 Sample data from first item:")
                        for key, value in list(first_item.items())[:3]:
                            if isinstance(value, str) and len(value) > 100:
                                print(f"   - {key}: {value[:100]}...")
                            else:
                                print(f"   - {key}: {value}")
            elif isinstance(results_data, dict):
                print(f"   - Data type: Dictionary")
                print(f"   - Top-level keys: {list(results_data.keys())}")
                
                # Check for nested data
                for key in ['data', 'results', 'crawled_data']:
                    if key in results_data:
                        nested_data = results_data[key]
                        if isinstance(nested_data, list):
                            print(f"   - {key}: List with {len(nested_data)} items")
                            if nested_data and isinstance(nested_data[0], dict):
                                print(f"   - Sample keys in {key}: {list(nested_data[0].keys())}")
            else:
                print(f"   - Data type: {type(results_data)}")
                
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON: {e}")
            print(f"   - First 200 chars: {results_text[:200]}")
    else:
        print(f"❌ Job results failed! Status: {results_response.status_code}")
        print(f"   - Response: {results_response.text[:200]}")

if __name__ == "__main__":
    print("🧪 Frontend Data Debug Tool")
    print("=" * 50)
    test_backend_data()
    print("\n" + "=" * 50)
    print("🎉 Debug test complete!")
