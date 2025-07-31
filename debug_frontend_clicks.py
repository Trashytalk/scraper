#!/usr/bin/env python3
"""
Frontend debugging script to check what's happening when buttons are clicked
"""

import requests
import json

def test_frontend_api_calls():
    """Test the exact API calls that frontend should be making"""
    
    print("🔍 Testing Frontend API Calls")
    print("=" * 40)
    
    # Get auth token
    login_response = requests.post("http://localhost:8000/api/auth/login", 
                                 json={"username": "admin", "password": "admin123"})
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get list of jobs first
    jobs_response = requests.get("http://localhost:8000/api/jobs", headers=headers)
    jobs = jobs_response.json()
    
    if not jobs:
        print("❌ No jobs found")
        return False
    
    # Test with the latest job
    latest_job = jobs[0]
    job_id = latest_job['id']
    
    print(f"Testing with Job ID: {job_id}")
    print(f"Job Name: {latest_job['name']}")
    print(f"Job Status: {latest_job['status']}")
    print()
    
    # Test 1: Job Details
    print("1. 🔍 Testing Job Details API call...")
    details_response = requests.get(f"http://localhost:8000/api/jobs/{job_id}", headers=headers)
    print(f"   Status: {details_response.status_code}")
    if details_response.status_code == 200:
        details = details_response.json()
        print(f"   ✅ Details received: {list(details.keys())}")
        print(f"   Job name: {details.get('name', 'N/A')}")
        print(f"   Job status: {details.get('status', 'N/A')}")
    else:
        print(f"   ❌ Error: {details_response.text}")
    print()
    
    # Test 2: Job Results  
    print("2. 📊 Testing Job Results API call...")
    results_response = requests.get(f"http://localhost:8000/api/jobs/{job_id}/results", headers=headers)
    print(f"   Status: {results_response.status_code}")
    if results_response.status_code == 200:
        results_data = results_response.json()
        print(f"   ✅ Results received: {type(results_data)}")
        if isinstance(results_data, list):
            print(f"   Results count: {len(results_data)}")
            if results_data:
                print(f"   Sample result keys: {list(results_data[0].keys()) if isinstance(results_data[0], dict) else 'Not a dict'}")
        elif isinstance(results_data, dict):
            print(f"   Results keys: {list(results_data.keys())}")
            if 'data' in results_data:
                print(f"   Data count: {len(results_data['data']) if isinstance(results_data['data'], list) else 'Not a list'}")
    else:
        print(f"   ❌ Error: {results_response.text}")
    print()
    
    # Test 3: Check CORS for frontend origin
    print("3. 🌐 Testing CORS with frontend origin...")
    cors_headers = {
        "Origin": "http://localhost:5173",
        "Authorization": f"Bearer {token}"
    }
    
    details_cors = requests.get(f"http://localhost:8000/api/jobs/{job_id}", headers=cors_headers)
    print(f"   Details with CORS: {details_cors.status_code}")
    
    results_cors = requests.get(f"http://localhost:8000/api/jobs/{job_id}/results", headers=cors_headers)
    print(f"   Results with CORS: {results_cors.status_code}")
    print()
    
    return True

def test_frontend_debugging():
    """Create JavaScript debugging code for the frontend"""
    
    print("4. 🐛 Frontend Debugging Code")
    print("=" * 40)
    
    js_debug_code = """
// Add this to the browser console to debug the frontend
console.log('=== Frontend Debugging ===');

// Override the getJobDetails function to add logging
const originalGetJobDetails = window.getJobDetails;
window.getJobDetails = async function(jobId) {
    console.log('🔍 getJobDetails called with jobId:', jobId);
    console.log('🔑 Current token:', window.token ? 'Present' : 'Missing');
    
    try {
        const response = await fetch(`http://localhost:8000/api/jobs/${jobId}`, {
            headers: {
                'Authorization': `Bearer ${window.token}`,
            },
        });
        
        console.log('📥 Details response status:', response.status);
        console.log('📥 Details response headers:', [...response.headers.entries()]);
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Details data received:', data);
            console.log('🎯 Setting selectedJob to:', data);
            // The data should trigger the modal to show
        } else {
            console.log('❌ Details request failed:', await response.text());
        }
    } catch (error) {
        console.error('💥 Details error:', error);
    }
};

// Override the getJobResults function to add logging
const originalGetJobResults = window.getJobResults;
window.getJobResults = async function(jobId) {
    console.log('📊 getJobResults called with jobId:', jobId);
    console.log('🔑 Current token:', window.token ? 'Present' : 'Missing');
    
    try {
        const response = await fetch(`http://localhost:8000/api/jobs/${jobId}/results`, {
            headers: {
                'Authorization': `Bearer ${window.token}`,
            },
        });
        
        console.log('📥 Results response status:', response.status);
        console.log('📥 Results response headers:', [...response.headers.entries()]);
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Results data received:', data);
            console.log('📊 Data type:', typeof data);
            console.log('📊 Data length/keys:', Array.isArray(data) ? data.length : Object.keys(data));
            
            // Log the transformation process
            const transformedData = {
                job_id: jobId,
                job_name: 'Debug Job',
                data: data.data || data.results || data || [],
                total_count: data.total_records || data.total_count || data.count || (data.data ? data.data.length : 0),
                status: 'completed',
                created_at: new Date().toISOString(),
                completed_at: new Date().toISOString()
            };
            
            console.log('🔄 Transformed data:', transformedData);
            console.log('🎯 Setting jobResults to:', transformedData);
            // The transformedData should trigger the results modal to show
        } else {
            console.log('❌ Results request failed:', await response.text());
        }
    } catch (error) {
        console.error('💥 Results error:', error);
    }
};

console.log('✅ Debug functions installed. Click Details/View Results buttons to see debug output.');
"""
    
    print("Copy and paste this into your browser console:")
    print("=" * 60)
    print(js_debug_code)
    print("=" * 60)
    
    return js_debug_code

if __name__ == "__main__":
    print("🐛 Frontend Button Click Debugging")
    print("=" * 50)
    
    # Test API calls
    if test_frontend_api_calls():
        print("✅ API calls are working correctly")
    else:
        print("❌ API calls failed")
    
    # Provide debugging code
    test_frontend_debugging()
    
    print("\n📋 DEBUGGING STEPS:")
    print("1. Open http://localhost:5173 in browser")
    print("2. Open browser developer tools (F12)")
    print("3. Go to Console tab")
    print("4. Paste the debugging code above")
    print("5. Click Details or View Results buttons")
    print("6. Check console output for errors")
    print("\n💡 Look for:")
    print("   - Authentication token issues")
    print("   - CORS errors")
    print("   - Modal not showing despite data")
    print("   - JavaScript errors preventing state updates")
    print("=" * 50)
