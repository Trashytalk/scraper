#!/usr/bin/env python3
"""Test progress bar functionality"""

import requests
import json
import sqlite3

def test_progress_api():
    # Get running job ID
    conn = sqlite3.connect('data/scraper.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, name FROM jobs WHERE status = "running" LIMIT 1')
    job_row = cursor.fetchone()
    
    if not job_row:
        print("❌ No running jobs found")
        return
    
    job_id, job_name = job_row
    print(f"🔍 Testing progress for job {job_id}: {job_name}")
    
    # Login to get token
    try:
        login_response = requests.post('http://localhost:8000/api/auth/login', 
                                    json={'username': 'admin', 'password': 'admin123'})
        
        if login_response.status_code == 200:
            token = login_response.json()['access_token']
            print(f"✅ Login successful, token: {token[:20]}...")
            
            # Test progress API
            headers = {'Authorization': f'Bearer {token}'}
            progress_response = requests.get(f'http://localhost:8000/api/jobs/{job_id}/progress', 
                                           headers=headers)
            
            print(f"📊 Progress API response: {progress_response.status_code}")
            
            if progress_response.status_code == 200:
                progress_data = progress_response.json()
                print("✅ Progress data:")
                print(json.dumps(progress_data, indent=2))
                
                # Check if progress is reasonable
                if 'progress_percentage' in progress_data:
                    print(f"📈 Progress: {progress_data['progress_percentage']}%")
                else:
                    print("❌ No progress_percentage in response")
            else:
                print(f"❌ Progress API error: {progress_response.text}")
                
        else:
            print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    conn.close()

if __name__ == "__main__":
    test_progress_api()
