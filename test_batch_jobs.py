#!/usr/bin/env python3
"""
Test script for batch job creation endpoint
"""

import json
import sys

import requests

# Configuration
BASE_URL = "http://localhost:8000"


def test_batch_jobs():
    """Test the batch job creation functionality"""

    print("🧪 Testing Batch Job Creation Endpoint")
    print("=" * 40)

    # Step 1: Login to get authentication token
    print("1. 🔐 Logging in...")
    login_data = {"username": "admin", "password": "admin123"}

    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False

        token = response.json().get("access_token")
        if not token:
            print("❌ No access token received")
            return False

        print("✅ Login successful")

    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error during login: {e}")
        return False

    # Step 2: Test batch job creation
    print("2. 📊 Creating batch jobs...")

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    batch_data = {
        "base_name": "Test Batch Scraping",
        "urls": [
            "https://example.com",
            "https://httpbin.org/get",
            "https://jsonplaceholder.typicode.com/posts/1",
        ],
        "scraper_type": "basic",
        "batch_size": 10,
        "config": {
            "timeout": 30,
            "custom_headers": {"User-Agent": "Business Intelligence Scraper Test"},
        },
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/jobs/batch", json=batch_data, headers=headers
        )

        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Batch job creation successful!")
            print(f"📊 Created {result.get('jobs_created', 0)} jobs")
            print(f"📝 Batch name: {result.get('batch_name', 'Unknown')}")

            # Show created jobs
            jobs = result.get("jobs", [])
            for i, job in enumerate(jobs, 1):
                print(
                    f"  Job {i}: {job.get('name')} - {job.get('url')} - Status: {job.get('status')}"
                )

            return True
        else:
            print(f"❌ Batch job creation failed: {response.status_code}")
            print(f"Error details: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error during batch job creation: {e}")
        return False


def test_api_docs():
    """Test if the API documentation includes the new endpoint"""
    print("3. 📖 Checking API documentation...")

    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ API documentation accessible")
            if "batch" in response.text.lower():
                print("✅ Batch endpoint appears in documentation")
            else:
                print("⚠️  Batch endpoint not found in documentation")
        else:
            print(f"❌ API documentation not accessible: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error accessing API documentation: {e}")


if __name__ == "__main__":
    print("🚀 Business Intelligence Scraper - Batch Job Test")
    print("=" * 50)

    # Test server connectivity
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and accessible")
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Make sure the server is running with: ./quick_start.sh")
        sys.exit(1)

    # Run tests
    success = test_batch_jobs()
    test_api_docs()

    print("\n" + "=" * 50)
    if success:
        print("🎉 Batch job functionality is working correctly!")
        print("✅ The NetworkError should now be resolved.")
    else:
        print("❌ Batch job functionality needs investigation.")
    print("=" * 50)
