#!/usr/bin/env python3
"""
Diagnose issues with progress bar and image viewing
"""

import requests
import json
import sqlite3
import os

def test_progress_api():
    """Test if the progress API is responding"""
    print("🔍 Testing Progress API...")
    
    try:
        # First get a list of recent jobs
        response = requests.get('http://localhost:8000/api/jobs', 
                              headers={'Authorization': f'Bearer {get_auth_token()}'})
        
        if response.status_code == 200:
            jobs = response.json()
            print(f"  ✅ Found {len(jobs)} jobs")
            
            if jobs:
                # Test progress API on the most recent job
                latest_job = jobs[0]
                job_id = latest_job['id']
                print(f"  Testing progress for job {job_id}")
                
                progress_response = requests.get(f'http://localhost:8000/api/jobs/{job_id}/progress',
                                               headers={'Authorization': f'Bearer {get_auth_token()}'})
                
                if progress_response.status_code == 200:
                    progress_data = progress_response.json()
                    print(f"  ✅ Progress API working: {progress_data['progress_percentage']}%")
                    return True
                else:
                    print(f"  ❌ Progress API error: {progress_response.status_code}")
                    return False
            else:
                print("  ⚠️  No jobs found to test progress")
                return True
        else:
            print(f"  ❌ Jobs API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Progress API test failed: {e}")
        return False

def test_image_assets():
    """Test image asset handling"""
    print("🖼️  Testing Image Assets...")
    
    try:
        # Check database for image data
        db_path = '/home/homebrew/scraper/data/scraper.db'
        if not os.path.exists(db_path):
            print(f"  ❌ Database not found: {db_path}")
            return False
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get recent jobs with results
        cursor.execute('''
            SELECT j.id, j.url, COUNT(jr.id) as result_count
            FROM jobs j 
            LEFT JOIN job_results jr ON j.id = jr.job_id 
            GROUP BY j.id 
            ORDER BY j.id DESC 
            LIMIT 5
        ''')
        
        jobs_with_results = cursor.fetchall()
        print(f"  Found {len(jobs_with_results)} recent jobs")
        
        for job_id, url, result_count in jobs_with_results:
            print(f"    Job {job_id}: {result_count} results - {url[:50]}...")
            
            if result_count > 0:
                # Check for image data in results
                cursor.execute('''
                    SELECT data FROM job_results 
                    WHERE job_id = ? 
                    LIMIT 1
                ''', (job_id,))
                
                result = cursor.fetchone()
                if result:
                    try:
                        data = json.loads(result[0])
                        if 'images' in data:
                            images = data['images']
                            print(f"      Images found: {len(images)}")
                            
                            # Check for placeholder images
                            placeholder_count = 0
                            for img in images:
                                url = img.get('url', '')
                                size = img.get('size', 0)
                                if 'placeholder' in url.lower() or size == 0:
                                    placeholder_count += 1
                            
                            if placeholder_count > 0:
                                print(f"      ⚠️  Placeholder/empty images: {placeholder_count}/{len(images)}")
                            else:
                                print(f"      ✅ All images have valid data")
                        else:
                            print("      No 'images' key in result data")
                    except json.JSONDecodeError:
                        print("      ❌ Could not parse result data as JSON")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"  ❌ Image asset test failed: {e}")
        return False

def test_network_diagram():
    """Test network diagram generation"""
    print("🕸️  Testing Network Diagram...")
    
    try:
        # Get a job with results and test network diagram
        response = requests.get('http://localhost:8000/api/jobs', 
                              headers={'Authorization': f'Bearer {get_auth_token()}'})
        
        if response.status_code == 200:
            jobs = response.json()
            
            for job in jobs[:3]:  # Test first 3 jobs
                job_id = job['id']
                
                # Test network diagram endpoint
                network_response = requests.get(f'http://localhost:8000/api/cfpl/network-diagram/{job_id}')
                
                if network_response.status_code == 200:
                    network_data = network_response.json()
                    nodes = network_data.get('nodes', [])
                    edges = network_data.get('edges', [])
                    
                    print(f"  Job {job_id}: {len(nodes)} nodes, {len(edges)} edges")
                    
                    if nodes:
                        # Check node titles
                        sample_node = nodes[0]
                        title = sample_node.get('data', {}).get('label', 'No title')
                        print(f"    Sample node title: {title[:50]}...")
                        
                        if edges:
                            print(f"    ✅ Network diagram generated successfully")
                        else:
                            print(f"    ⚠️  No edges found (isolated nodes)")
                    else:
                        print(f"    ❌ No nodes found in network diagram")
                else:
                    print(f"  Job {job_id}: Network diagram error {network_response.status_code}")
            
            return True
        else:
            print(f"  ❌ Could not fetch jobs: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Network diagram test failed: {e}")
        return False

def get_auth_token():
    """Get authentication token"""
    # For testing, try to use a stored token or create a test user
    return "test-token"  # This might need to be updated based on your auth setup

def main():
    """Run all diagnostic tests"""
    print("🔧 Running Diagnostic Tests for Issues")
    print("=" * 50)
    
    tests = [
        ("Progress Bar API", test_progress_api),
        ("Image Assets", test_image_assets), 
        ("Network Diagram", test_network_diagram),
    ]
    
    passed = 0
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        
    print("\n" + "=" * 50)
    print(f"📊 Diagnostic Results: {passed}/{len(tests)} tests passed")
    
    if passed < len(tests):
        print("\n🔧 Issues found. Checking specific problems...")
        
        # Check if this is a frontend integration issue
        print("\n💡 Suggested fixes:")
        print("1. Progress Bar: Check if frontend is calling /api/jobs/{job_id}/progress")
        print("2. Image Assets: Filter out placeholder images in frontend")
        print("3. Network Diagram: Check layout algorithms and node positioning")

if __name__ == "__main__":
    main()
