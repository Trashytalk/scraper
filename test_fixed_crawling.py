#!/usr/bin/env python3
"""
Test the fixed intelligent crawling by creating a job through the API
"""

import json
import os
import sys
import time

import requests

# Add the parent directory to the path to import config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config.environment import get_config, get_test_credentials


def test_fixed_crawling():
    """Test intelligent crawling through the API"""

    config = get_config()
    BASE_URL = config.API_BASE_URL
    credentials = get_test_credentials()

    print("🔧 Testing Fixed Intelligent Crawling")
    print("=" * 50)

    # Login first
    print("🔐 Logging in...")
    login_response = requests.post(f"{BASE_URL}/api/auth/login", json=credentials)

    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    print("✅ Login successful")

    # Create an intelligent crawling job
    print("\n🚀 Creating intelligent crawling job...")

    job_data = {
        "name": "Thailand Fixed Crawling Test",
        "type": "intelligent_crawling",
        "url": "https://en.wikipedia.org/wiki/Thailand",
        "scraper_type": "intelligent",
        "config": {
            "max_depth": 3,
            "max_pages": 10,
            "follow_internal_links": True,
            "follow_external_links": False,
            "rate_limit": {"requests_per_second": 1.5},
        },
    }

    create_response = requests.post(
        f"{BASE_URL}/api/jobs", json=job_data, headers=headers
    )

    if create_response.status_code != 201:
        print(f"❌ Job creation failed: {create_response.status_code}")
        print(f"Response: {create_response.text}")
        return

    job_info = create_response.json()
    job_id = job_info["id"]
    print(f"✅ Job created with ID: {job_id}")

    # Start the job
    print(f"\n▶️  Starting job {job_id}...")
    start_response = requests.post(
        f"{BASE_URL}/api/jobs/{job_id}/start", headers=headers
    )

    if start_response.status_code != 200:
        print(f"❌ Job start failed: {start_response.status_code}")
        print(f"Response: {start_response.text}")
        return

    print("✅ Job started successfully")

    # Monitor job progress
    print("\n⏳ Monitoring job progress...")
    for i in range(30):  # Wait up to 30 seconds
        time.sleep(1)

        # Check job status
        status_response = requests.get(f"{BASE_URL}/api/jobs/{job_id}", headers=headers)

        if status_response.status_code == 200:
            job_status = status_response.json()
            status = job_status.get("status", "unknown")
            results_count = job_status.get("results_count", 0)

            print(f"   Status: {status}, Results: {results_count}")

            if status == "completed":
                print(f"🎉 Job completed after {i+1} seconds!")

                # Get results
                print("\n📊 Fetching results...")
                results_response = requests.get(
                    f"{BASE_URL}/api/jobs/{job_id}/results", headers=headers
                )

                if results_response.status_code == 200:
                    results = results_response.json()

                    print(f"Results structure: {type(results)}")

                    if isinstance(results, dict):
                        # Check if it's intelligent crawling results
                        if "summary" in results:
                            summary = results["summary"]
                            print(f"📈 Crawling Summary:")
                            print(
                                f"   Pages processed: {summary.get('pages_processed', 0)}"
                            )
                            print(
                                f"   URLs discovered: {summary.get('urls_discovered', 0)}"
                            )
                            print(
                                f"   Data extracted: {summary.get('data_extracted', 0)}"
                            )

                            crawled_data = results.get("crawled_data", [])
                            print(f"   Crawled pages: {len(crawled_data)}")

                            if len(crawled_data) > 1:
                                print(f"🎯 SUCCESS: Multiple pages crawled!")
                                print(f"   Sample crawled URLs:")
                                for i, page in enumerate(crawled_data[:5]):
                                    url = page.get("url", "No URL")
                                    title = page.get("title", "No title")[:40]
                                    print(f"   {i+1}. {url}")
                                    print(f"      '{title}'")
                            else:
                                print(f"⚠️  Only {len(crawled_data)} page(s) crawled")

                        elif "url" in results:
                            print(f"❌ Got single page result instead of crawling:")
                            print(f"   URL: {results.get('url', 'N/A')}")
                            print(f"   Status: {results.get('status', 'N/A')}")
                            links = results.get("links", [])
                            print(f"   Links found: {len(links)}")

                    elif isinstance(results, list):
                        print(f"📄 Got {len(results)} result items")

                else:
                    print(f"❌ Failed to get results: {results_response.status_code}")

                break

            elif status == "failed":
                print(f"❌ Job failed!")
                error_msg = job_status.get("error_message", "Unknown error")
                print(f"   Error: {error_msg}")
                break

        else:
            print(f"❌ Failed to check job status: {status_response.status_code}")
            break
    else:
        print(f"⏰ Job did not complete within 30 seconds")


if __name__ == "__main__":
    test_fixed_crawling()
