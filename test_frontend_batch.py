#!/usr/bin/env python3
"""
Test script to verify frontend batch job creation is working
"""

import json
import time

import requests


def test_frontend_batch_creation():
    """Test that we can create batch jobs through frontend simulation"""

    print("🌐 Testing Frontend Batch Job Creation")
    print("=" * 45)

    # Step 1: Login via API (simulate frontend login)
    print("1. 🔐 Logging in via API...")
    login_data = {"username": "admin", "password": "admin123"}

    try:
        response = requests.post(
            "http://localhost:8000/api/auth/login", json=login_data
        )
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            return False

        token = response.json().get("access_token")
        print("✅ Login successful")

    except Exception as e:
        print(f"❌ Login error: {e}")
        return False

    # Step 2: Test batch job creation with BBC URL
    print("2. 📊 Creating batch job with BBC Business URL...")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "http://localhost:5173",  # Frontend origin
        "Referer": "http://localhost:5173/",
    }

    # Data similar to what frontend would send
    batch_data = {
        "base_name": "BBC Business Scraping from Frontend",
        "urls": [
            "https://www.bbc.com/business",
            "https://www.bbc.com/news/business",
        ],
        "scraper_type": "basic",
        "batch_size": 10,
        "config": {
            "timeout": 30,
            "user_agent": "Business Intelligence Scraper Frontend",
        },
    }

    try:
        # This simulates the exact call the frontend should make
        response = requests.post(
            "http://localhost:8000/api/jobs/batch", json=batch_data, headers=headers
        )

        print(f"Response Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Frontend batch job creation successful!")
            print(f"📊 Created {result.get('jobs_created', 0)} jobs")
            print(f"📝 Batch name: {result.get('batch_name')}")

            # Show created jobs
            jobs = result.get("jobs", [])
            for i, job in enumerate(jobs, 1):
                print(f"  Job {i}: {job.get('name')} - {job.get('url')}")

            return True
        else:
            print(f"❌ Batch job creation failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Network error: {e}")
        print("This is the type of error you were seeing!")
        return False


def test_frontend_connectivity():
    """Test that frontend and backend can communicate"""
    print("3. 🔗 Testing Frontend-Backend Communication")
    print("=" * 45)

    # Test frontend is accessible
    try:
        response = requests.get("http://localhost:5173", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend accessible at http://localhost:5173")
        else:
            print(f"⚠️  Frontend responded with status: {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend not accessible: {e}")

    # Test backend is accessible
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend accessible at http://localhost:8000")
        else:
            print(f"⚠️  Backend responded with status: {response.status_code}")
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")

    # Test CORS
    try:
        response = requests.options(
            "http://localhost:8000/api/jobs/batch",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type,Authorization",
            },
        )

        if response.status_code == 200:
            cors_origin = response.headers.get("access-control-allow-origin", "Not set")
            print(f"✅ CORS configured: {cors_origin}")
        else:
            print(f"⚠️  CORS preflight failed: {response.status_code}")
    except Exception as e:
        print(f"❌ CORS check failed: {e}")


if __name__ == "__main__":
    print("🚀 Frontend Batch Job Testing")
    print("=" * 50)

    # Test connectivity first
    test_frontend_connectivity()
    print()

    # Test batch job creation
    success = test_frontend_batch_creation()

    print("\n" + "=" * 50)
    if success:
        print("🎉 SUCCESS: Frontend batch job creation is working!")
        print("✅ The NetworkError should now be resolved.")
        print("\n📋 Next steps:")
        print("1. Open http://localhost:5173 in your browser")
        print("2. Login with admin/admin123")
        print("3. Try creating batch jobs with BBC Business URL")
        print("4. The NetworkError should no longer occur")
    else:
        print("❌ FAILURE: Still experiencing issues")
        print("Additional debugging may be needed")
    print("=" * 50)
