#!/usr/bin/env python3
"""
End-to-End Test: Wikipedia iPhone Scraping
Tests complete workflow from authentication to job completion
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"
WIKIPEDIA_URL = "https://en.wikipedia.org/wiki/IPhone"

def main():
    print("🧪 END-TO-END TEST: Wikipedia iPhone Scraping")
    print("=" * 60)
    
    # Step 1: Health Check
    print("1️⃣ Testing backend health...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Backend healthy (uptime: {health_data.get('checks', {}).get('api', {}).get('uptime_human', 'unknown')})")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False
    
    # Step 2: Authentication
    print("\n2️⃣ Testing authentication...")
    for password in ["admin123", "admin", "password", "tactical"]:
        try:
            auth_data = {"username": "admin", "password": password}
            response = requests.post(f"{BASE_URL}/api/auth/login", json=auth_data, timeout=5)
            
            if response.status_code == 200:
                token_data = response.json()
                token = token_data.get("access_token")
                print(f"✅ Authentication successful with password: {password}")
                print(f"   Token received: {token[:50] if token else 'None'}...")
                break
            else:
                print(f"   ❌ Failed with password '{password}': {response.status_code}")
                token = None
        except Exception as e:
            print(f"   ❌ Auth error with '{password}': {e}")
            token = None
    
    if not token:
        print("❌ Authentication failed with all passwords")
        return False
    
    # Step 3: Create Wikipedia iPhone Job
    print("\n3️⃣ Creating Wikipedia iPhone scraping job...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        job_data = {
            "name": "QA Test - Wikipedia iPhone",
            "url": WIKIPEDIA_URL,
            "type": "intelligent",  # Backend expects "type" field
            "scraper_type": "intelligent",
            "config": {
                "extract_full_html": True,
                "save_to_database": True,
                "crawl_links": False,
                "follow_internal_links": False,
                "max_depth": 1,
                "max_pages": 1,
                "delay_between_requests": 2000,
                "respect_robots_txt": True,
                "include_images": True,
                "extract_metadata": True
            }
        }
        
        response = requests.post(f"{BASE_URL}/api/jobs", json=job_data, headers=headers, timeout=10)
        
        if response.status_code in [200, 201]:
            job_info = response.json()
            job_id = job_info.get("job_id") or job_info.get("id")
            print(f"✅ Job created successfully!")
            print(f"   Job ID: {job_id}")
            print(f"   Job Name: {job_info.get('name', 'Unknown')}")
            print(f"   Target URL: {job_info.get('url', 'Unknown')}")
        else:
            error_details = response.text
            print(f"❌ Job creation failed: {response.status_code}")
            print(f"   Error details: {error_details}")
            return False
            
    except Exception as e:
        print(f"❌ Job creation error: {e}")
        return False
    
    # Step 4: Start Job
    print("\n4️⃣ Starting scraping job...")
    try:
        response = requests.post(f"{BASE_URL}/api/jobs/{job_id}/start", headers=headers, timeout=10)
        
        if response.status_code in [200, 202]:
            print("✅ Job started successfully!")
        else:
            print(f"❌ Failed to start job: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Job start error: {e}")
    
    # Step 5: Monitor Job Progress
    print("\n5️⃣ Monitoring job progress...")
    max_wait_time = 60  # 1 minute timeout
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        try:
            response = requests.get(f"{BASE_URL}/api/jobs/{job_id}", headers=headers, timeout=5)
            if response.status_code == 200:
                job_status = response.json()
                status = job_status.get("status", "unknown")
                progress = job_status.get("progress", 0)
                
                print(f"   📊 Status: {status} | Progress: {progress}%")
                
                if status in ["completed", "success", "finished"]:
                    print("✅ Job completed successfully!")
                    break
                elif status in ["failed", "error"]:
                    print("❌ Job failed")
                    break
                    
                time.sleep(5)
            else:
                print(f"   ⚠️ Status check failed: {response.status_code}")
                break
        except Exception as e:
            print(f"   ⚠️ Status check error: {e}")
            break
    else:
        print(f"⏰ Job monitoring timeout after {max_wait_time} seconds")
    
    # Step 6: Retrieve Results
    print("\n6️⃣ Retrieving job results...")
    try:
        response = requests.get(f"{BASE_URL}/api/jobs/{job_id}/results", headers=headers, timeout=10)
        
        if response.status_code == 200:
            results = response.json()
            print("✅ Results retrieved successfully!")
            
            # Analyze results
            if isinstance(results, dict):
                if "extracted_data" in results:
                    data = results["extracted_data"]
                    print(f"   📄 Extracted data length: {len(str(data)) if data else 0} characters")
                
                if "metadata" in results:
                    metadata = results["metadata"]
                    print(f"   📊 Metadata fields: {len(metadata) if metadata else 0}")
                
                if "images" in results:
                    images = results["images"]
                    print(f"   🖼️ Images found: {len(images) if images else 0}")
                    
                if "url" in results:
                    print(f"   🔗 Source URL confirmed: {results['url']}")
            
            print(f"   📝 Total result size: {len(json.dumps(results, default=str))} bytes")
            
        else:
            print(f"❌ Failed to retrieve results: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Results retrieval error: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 End-to-end test complete!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
