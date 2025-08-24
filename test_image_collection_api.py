#!/usr/bin/env python3
"""
Test image collection via API to verify the complete flow
"""

import requests
import json
import time


def test_image_collection():
    """Test image collection through the API"""
    base_url = "http://localhost:8000"
    
    # Login first
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    print("🔐 Logging in...")
    login_response = requests.post(f"{base_url}/api/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Login successful")
    
    # Create a job with image collection enabled
    job_data = {
        "name": "Image Collection Test",
        "url": "https://en.wikipedia.org/wiki/Web_scraping",
        "type": "intelligent",
        "scraper_type": "basic",
        "config": {
            "include_images": True,
            "max_pages": 1,
            "save_to_database": True
        }
    }
    
    print("🔧 Creating job with image collection...")
    job_response = requests.post(f"{base_url}/api/jobs", json=job_data, headers=headers)
    
    if job_response.status_code not in [200, 201]:
        print(f"❌ Job creation failed: {job_response.status_code}")
        print(job_response.text)
        return
    
    response_data = job_response.json()
    job_id = response_data.get("id") or response_data.get("job_id")
    print(f"✅ Job created with ID: {job_id}")
    
    # Wait for job completion
    print("⏳ Waiting for job completion...")
    for i in range(30):  # Wait up to 30 seconds
        time.sleep(1)
        progress_response = requests.get(f"{base_url}/api/jobs/{job_id}/progress", headers=headers)
        
        if progress_response.status_code == 200:
            progress = progress_response.json()
            print(f"   Progress: {progress.get('status', 'unknown')} - {progress.get('progress_percentage', 0)}%")
            
            if progress.get('status') == 'completed':
                break
        else:
            print(f"   Error getting progress: {progress_response.status_code}")
    
    # Get results
    print("📊 Getting job results...")
    results_response = requests.get(f"{base_url}/api/jobs/{job_id}/results", headers=headers)
    
    if results_response.status_code != 200:
        print(f"❌ Failed to get results: {results_response.status_code}")
        return
    
    results = results_response.json()
    print(f"✅ Results retrieved")
    
    # Analyze image collection
    if "data" in results and results["data"]:
        total_images = 0
        for result in results["data"]:
            if "images" in result:
                image_count = len(result["images"])
                total_images += image_count
                print(f"   📄 {result.get('url', 'Unknown URL')}: {image_count} images")
                
                # Show first few images
                if result["images"]:
                    print(f"      🖼️ Sample images:")
                    for i, img in enumerate(result["images"][:3]):
                        print(f"         {i+1}. {img.get('src', 'No src')} (alt: {img.get('alt', 'No alt')})")
        
        print(f"\n📊 Summary:")
        print(f"   Total Results: {len(results['data'])}")
        print(f"   Total Images Collected: {total_images}")
        
        if total_images > 0:
            print("✅ Image collection is working correctly!")
        else:
            print("❌ No images were collected")
    else:
        print("❌ No data in results")


if __name__ == "__main__":
    test_image_collection()
