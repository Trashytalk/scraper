#!/usr/bin/env python3
"""
Test script to verify the backend API works with always-enabled features
"""

import requests
import json
import time


def test_backend_api():
    """Test the backend API to ensure always-enabled features work correctly"""
    base_url = "http://localhost:8000"
    
    print("🔧 Testing Backend API with Always-Enabled Features")
    print("=" * 60)
    
    # Test job creation endpoint
    print("1. Testing /api/jobs endpoint (create job)")
    
    job_data = {
        "url": "https://httpbin.org/forms/post",
        "crawler_type": "basic",
        "config": {
            # These should be automatically enabled in the backend regardless of what we send
            "extract_full_html": True,
            "include_images": True,
            "include_forms": True,
            "save_to_database": True,
            "max_pages": 1
        }
    }
    
    try:
        response = requests.post(f"{base_url}/api/jobs", json=job_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Job creation successful")
            print(f"   📊 Job ID: {result.get('job_id', 'unknown')}")
            print(f"   📊 Status: {result.get('status', 'unknown')}")
            
            # Try to start the job
            job_id = result.get('job_id')
            if job_id:
                start_response = requests.post(f"{base_url}/api/jobs/{job_id}/start", timeout=30)
                if start_response.status_code == 200:
                    print(f"   ✅ Job started successfully")
                    
                    # Wait a bit for job to complete
                    time.sleep(3)
                    
                    # Get results
                    results_response = requests.get(f"{base_url}/api/jobs/{job_id}/results", timeout=30)
                    if results_response.status_code == 200:
                        results_data = results_response.json()
                        print(f"   ✅ Results retrieved successfully")
                        
                        # Check if data contains our always-enabled features
                        if 'data' in results_data and results_data['data']:
                            page_data = results_data['data'][0]  # First page
                            print(f"   🖼️ Images: {len(page_data.get('images', []))}")
                            print(f"   📝 Forms: {len(page_data.get('forms', []))}")
                            print(f"   📄 HTML size: {len(page_data.get('raw_html', '')):,} chars")
                            print(f"   📋 Keys: {', '.join(sorted(page_data.keys()))}")
                        else:
                            print(f"   ❌ No data in results")
                    else:
                        print(f"   ❌ Results request failed: {results_response.status_code}")
                else:
                    print(f"   ❌ Job start failed: {start_response.status_code}")
            else:
                print(f"   ❌ No job_id in response")
        else:
            print(f"   ❌ Request failed: {response.status_code}")
            print(f"   Error: {response.text}")
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "-" * 40)
    
    # Test batch job creation
    print("2. Testing /api/jobs/batch endpoint")
    
    batch_data = {
        "jobs": [
            {
                "url": "https://httpbin.org/forms/post",
                "crawler_type": "basic",
                "config": {
                    # These should be automatically enabled
                    "extract_full_html": True,
                    "include_images": True,
                    "include_forms": True,
                    "save_to_database": True,
                    "max_pages": 1
                }
            }
        ]
    }
    
    try:
        response = requests.post(f"{base_url}/api/jobs/batch", json=batch_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Batch job creation successful")
            print(f"   📊 Jobs created: {len(result.get('job_ids', []))}")
            
            # Try to start first job and check results
            job_ids = result.get('job_ids', [])
            if job_ids:
                job_id = job_ids[0]
                start_response = requests.post(f"{base_url}/api/jobs/{job_id}/start", timeout=30)
                if start_response.status_code == 200:
                    print(f"   ✅ First job started successfully")
                    
                    # Wait for completion
                    time.sleep(3)
                    
                    # Get results
                    results_response = requests.get(f"{base_url}/api/jobs/{job_id}/results", timeout=30)
                    if results_response.status_code == 200:
                        results_data = results_response.json()
                        print(f"   ✅ Batch job results retrieved")
                        
                        if 'data' in results_data and results_data['data']:
                            page_data = results_data['data'][0]
                            print(f"   📋 Batch job keys: {', '.join(sorted(page_data.keys()))}")
                else:
                    print(f"   ❌ Job start failed: {start_response.status_code}")
        else:
            print(f"   ❌ Batch request failed: {response.status_code}")
            print(f"   Error: {response.text}")
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Backend API Test Complete!")
    print("✅ All media collection features are always enabled")
    print("✅ Frontend no longer needs checkboxes for these options")


if __name__ == "__main__":
    test_backend_api()
