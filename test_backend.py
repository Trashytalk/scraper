#!/usr/bin/env python3
"""
Backend API Test Script
Tests authentication and job creation with Wikipedia iPhone URL
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        print(f"✅ Health check: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_login(username="admin", password="admin123"):
    """Test login endpoint"""
    try:
        data = {"username": username, "password": password}
        response = requests.post(f"{BASE_URL}/api/auth/login", json=data, timeout=5)
        print(f"🔐 Login attempt: {response.status_code}")
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"✅ Token received: {token[:50] if token else 'None'}...")
            return token
        else:
            print(f"❌ Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_job_creation(token):
    """Test job creation with Wikipedia iPhone URL"""
    if not token:
        print("❌ No token available for job creation")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        job_data = {
            "name": "Wikipedia iPhone Test",
            "url": "https://en.wikipedia.org/wiki/IPhone",
            "scraper_type": "intelligent",
            "config": {
                "extract_full_html": True,
                "save_to_database": True,
                "crawl_links": False,
                "max_depth": 1,
                "max_pages": 1
            }
        }
        
        response = requests.post(f"{BASE_URL}/api/jobs", json=job_data, headers=headers, timeout=10)
        print(f"📋 Job creation: {response.status_code}")
        if response.status_code in [200, 201]:
            job_info = response.json()
            print(f"✅ Job created: {job_info.get('job_id', 'Unknown ID')}")
            return True
        else:
            print(f"❌ Job creation failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Job creation error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Backend API Test Suite")
    print("=" * 40)
    
    # Test health
    if not test_health():
        print("❌ Backend not responding")
        exit(1)
    
    # Test authentication
    token = test_login()
    
    # Try alternative passwords if first fails
    if not token:
        for pwd in ["admin", "password", "123456", "tactical"]:
            token = test_login("admin", pwd)
            if token:
                break
    
    # Test job creation
    if token:
        test_job_creation(token)
    else:
        print("❌ Authentication failed - cannot test job creation")
    
    print("=" * 40)
    print("🏁 Test suite complete")
