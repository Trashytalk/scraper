#!/usr/bin/env python3
"""
Test the complete crawling pipeline via API
"""

import json
import time

import requests

API_BASE = "http://localhost:8000"


def test_crawling_pipeline():
    print("🔍 Testing Complete Crawling Pipeline via API")
    print("=" * 50)

    # Step 1: Login
    print("\n1. Logging in...")
    login_data = {"username": "admin", "password": "admin123"}

    login_response = requests.post(f"{API_BASE}/api/auth/login", json=login_data)
    if login_response.status_code != 200:
        print(f"   ❌ Login failed: {login_response.status_code}")
        return

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("   ✅ Login successful")

    # Step 2: Create crawling job
    print("\n2. Creating intelligent crawling job...")
    job_data = {
        "name": "Test HTTPBin Crawling",
        "type": "intelligent_crawling",
        "url": "https://httpbin.org",
        "scraper_type": "intelligent",
        "config": {
            "max_pages": 5,
            "max_depth": 2,
            "follow_internal_links": True,
            "follow_external_links": True,
            "rate_limit": {"requests_per_second": 2.0},
        },
    }

    job_response = requests.post(f"{API_BASE}/api/jobs", json=job_data, headers=headers)
    if job_response.status_code != 200:
        print(f"   ❌ Job creation failed: {job_response.status_code}")
        print(f"   Response: {job_response.text}")
        return

    job_id = job_response.json()["id"]
    print(f"   ✅ Job created with ID: {job_id}")

    # Step 3: Start the job
    print("\n3. Starting the job...")
    start_response = requests.post(
        f"{API_BASE}/api/jobs/{job_id}/start", headers=headers
    )
    if start_response.status_code != 200:
        print(f"   ❌ Job start failed: {start_response.status_code}")
        print(f"   Response: {start_response.text}")
        return

    print("   ✅ Job started")

    # Step 4: Monitor job progress
    print("\n4. Monitoring job progress...")
    max_wait_time = 60  # seconds
    start_time = time.time()

    while time.time() - start_time < max_wait_time:
        jobs_response = requests.get(f"{API_BASE}/api/jobs", headers=headers)
        if jobs_response.status_code == 200:
            jobs = jobs_response.json()
            current_job = next((j for j in jobs if j["id"] == job_id), None)

            if current_job:
                status = current_job["status"]
                print(f"   Job status: {status}")

                if "summary" in current_job:
                    summary = current_job["summary"]
                    print(f"   Summary: {summary}")

                if status == "completed":
                    print("   ✅ Job completed successfully!")

                    # Step 5: Get results
                    print("\n5. Fetching results...")
                    results_response = requests.get(
                        f"{API_BASE}/api/jobs/{job_id}/results", headers=headers
                    )
                    if results_response.status_code == 200:
                        results = results_response.json()
                        print(f"   ✅ Results retrieved")

                        if isinstance(results, dict) and "summary" in results:
                            print(f"   Summary: {results['summary']}")

                        if isinstance(results, dict) and "crawled_data" in results:
                            print(f"   Crawled pages: {len(results['crawled_data'])}")
                            print(
                                f"   Discovered URLs: {len(results.get('discovered_urls', []))}"
                            )

                        return results
                    else:
                        print(
                            f"   ❌ Failed to get results: {results_response.status_code}"
                        )
                    break
                elif status == "failed":
                    print("   ❌ Job failed")
                    break

        time.sleep(2)

    print("   ⏰ Job monitoring timed out")


if __name__ == "__main__":
    test_crawling_pipeline()
