#!/usr/bin/env python3
"""
Quick API Test for Running Backend Server

This test checks if the backend server is accessible and responding.
"""

import requests
import json
import sys
from pathlib import Path

def test_server_health():
    """Test if the server is accessible"""
    print("🌐 Testing Server Health")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    try:
        # Test basic server response
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"Health check status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Server is responding")
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"⚠️ Server responded with status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server (not running or not accessible)")
        return False
    except requests.exceptions.Timeout:
        print("❌ Server response timeout")
        return False
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        return False
    
    return True

def test_api_endpoints():
    """Test basic API endpoints"""
    print("\n🔗 Testing API Endpoints")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    endpoints_to_test = [
        "/",
        "/docs",
        "/api/health",
        "/api/status"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK ({response.status_code})")
            elif response.status_code == 404:
                print(f"⚠️ {endpoint} - Not Found ({response.status_code})")
            else:
                print(f"⚠️ {endpoint} - Status {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")

def test_authentication():
    """Test authentication endpoint"""
    print("\n🔐 Testing Authentication")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    try:
        # Test login endpoint
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        response = requests.post(f"{base_url}/api/auth/login", json=login_data, timeout=5)
        print(f"Login attempt status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Authentication endpoint working")
            data = response.json()
            if "access_token" in data:
                print("✅ Token generated successfully")
                return data["access_token"]
            else:
                print("⚠️ No access token in response")
        else:
            print(f"⚠️ Authentication failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Authentication test error: {e}")
    
    return None

def test_with_token(token):
    """Test authenticated endpoints"""
    print("\n🔑 Testing Authenticated Endpoints")
    print("=" * 40)
    
    if not token:
        print("❌ No token available for authenticated tests")
        return
    
    base_url = "http://localhost:8000"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    protected_endpoints = [
        "/api/users/me",
        "/api/dashboard/stats",
        "/api/crawl/jobs"
    ]
    
    for endpoint in protected_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK (authenticated)")
            elif response.status_code == 401:
                print(f"⚠️ {endpoint} - Unauthorized (may need different credentials)")
            elif response.status_code == 404:
                print(f"⚠️ {endpoint} - Not Found")
            else:
                print(f"⚠️ {endpoint} - Status {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")

def main():
    """Run all API tests"""
    print("🧪 QUICK API TESTING SUITE")
    print("=" * 50)
    
    # Test server health
    if not test_server_health():
        print("\n❌ Server is not accessible. Cannot run API tests.")
        sys.exit(1)
    
    # Test basic endpoints
    test_api_endpoints()
    
    # Test authentication
    token = test_authentication()
    
    # Test authenticated endpoints
    test_with_token(token)
    
    print("\n🎯 API Test Summary:")
    print("Basic connectivity and endpoint tests completed!")
    print("For comprehensive testing, use: ./run_tests.sh api")

if __name__ == "__main__":
    main()
