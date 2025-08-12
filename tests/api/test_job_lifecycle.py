#!/usr/bin/env python3
"""
Test script to debug job execution and result retrieval issues
"""

import json
import time

import requests


def get_auth_token():
    """Get authentication token"""
    login_data = {"username": "admin", "password": "admin123"}
    response = requests.post("http://localhost:8000/api/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json().get("access_token")
    return None


def test_job_lifecycle():
    """Test complete job lifecycle: create -> start -> check status -> get results"""

    print("🔄 Testing Complete Job Lifecycle")
    print("=" * 50)

    token = get_auth_token()
    if not token:
        print("❌ Failed to get auth token")
        return False

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Step 1: Create a single job first
    print("1. 📝 Creating a test job...")
    job_data = {
        "name": "BBC Business Test Job",
        "type": "scraping",
        "url": "https://www.bbc.com/business",
        "scraper_type": "basic",
        "config": {"timeout": 30, "user_agent": "Business Intelligence Scraper Test"},
    }

    try:
        response = requests.post(
            "http://localhost:8000/api/jobs", json=job_data, headers=headers
        )
        if response.status_code != 200:
            print(f"❌ Job creation failed: {response.status_code} - {response.text}")
            return False

        job_id = response.json().get("id")
        print(f"✅ Job created with ID: {job_id}")

    except Exception as e:
        print(f"❌ Error creating job: {e}")
        return False

    # Step 2: Check job details before starting
    print(f"2. 👁️  Getting job details for ID {job_id}...")
    try:
        response = requests.get(
            f"http://localhost:8000/api/jobs/{job_id}", headers=headers
        )
        print(f"Job details response status: {response.status_code}")
        if response.status_code == 200:
            job_details = response.json()
            print(f"✅ Job details retrieved:")
            print(f"   Name: {job_details.get('name', 'N/A')}")
            print(f"   Status: {job_details.get('status', 'N/A')}")
            print(f"   URL: {job_details.get('url', 'N/A')}")
        else:
            print(f"❌ Failed to get job details: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error getting job details: {e}")
        return False

    # Step 3: Start the job
    print(f"3. 🚀 Starting job {job_id}...")
    try:
        response = requests.post(
            f"http://localhost:8000/api/jobs/{job_id}/start", headers=headers
        )
        print(f"Job start response status: {response.status_code}")
        if response.status_code == 200:
            start_result = response.json()
            print(f"✅ Job start initiated: {start_result.get('message', 'Started')}")
        else:
            print(f"❌ Failed to start job: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error starting job: {e}")
        return False

    # Step 4: Wait and check status periodically
    print("4. ⏳ Monitoring job execution...")
    max_wait = 30  # Wait up to 30 seconds
    wait_time = 0

    while wait_time < max_wait:
        try:
            response = requests.get(
                f"http://localhost:8000/api/jobs/{job_id}", headers=headers
            )
            if response.status_code == 200:
                job_status = response.json()
                status = job_status.get("status", "unknown")
                print(f"   Status check ({wait_time}s): {status}")

                if status in ["completed", "failed"]:
                    print(f"✅ Job finished with status: {status}")
                    break
                elif status == "running":
                    print(f"   Job is running... waiting...")

            time.sleep(2)
            wait_time += 2
        except Exception as e:
            print(f"❌ Error checking job status: {e}")
            break

    # Step 5: Try to get results
    print(f"5. 📊 Getting job results for ID {job_id}...")
    try:
        response = requests.get(
            f"http://localhost:8000/api/jobs/{job_id}/results", headers=headers
        )
        print(f"Results response status: {response.status_code}")
        print(f"Results response headers: {dict(response.headers)}")

        if response.status_code == 200:
            results = response.json()
            print(f"✅ Results retrieved successfully!")
            print(f"   Results type: {type(results)}")
            print(
                f"   Results keys: {list(results.keys()) if isinstance(results, dict) else 'Not a dict'}"
            )

            # Show some sample data
            if isinstance(results, dict):
                if "results" in results:
                    results_data = results["results"]
                    print(
                        f"   Results count: {len(results_data) if isinstance(results_data, list) else 'Not a list'}"
                    )
                    if isinstance(results_data, list) and results_data:
                        print(f"   Sample result: {str(results_data[0])[:200]}...")
                elif "data" in results:
                    print(f"   Data field: {str(results['data'])[:200]}...")
                else:
                    print(f"   Full results: {str(results)[:200]}...")

            return True
        else:
            print(f"❌ Failed to get results: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error getting results: {e}")
        return False


def test_database_inspection():
    """Check what's actually in the database"""
    print("\n6. 🔍 Inspecting Database Contents")
    print("=" * 40)

    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Get all jobs
    try:
        response = requests.get("http://localhost:8000/api/jobs", headers=headers)
        if response.status_code == 200:
            jobs = response.json()
            print(f"✅ Total jobs in database: {len(jobs)}")

            for job in jobs[-5:]:  # Show last 5 jobs
                job_id = job.get("id")
                name = job.get("name", "N/A")
                status = job.get("status", "N/A")
                results_count = job.get("results_count", 0)
                print(
                    f"   Job {job_id}: {name[:30]}... | Status: {status} | Results: {results_count}"
                )
        else:
            print(f"❌ Failed to get jobs list: {response.text}")
    except Exception as e:
        print(f"❌ Error getting jobs: {e}")


def test_results_endpoints():
    """Test different ways to get results"""
    print("\n7. 🎯 Testing Results Endpoints")
    print("=" * 40)

    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Get recent jobs and test their results
    try:
        response = requests.get("http://localhost:8000/api/jobs", headers=headers)
        if response.status_code == 200:
            jobs = response.json()

            # Test results for completed jobs
            for job in jobs[-3:]:  # Check last 3 jobs
                job_id = job.get("id")
                status = job.get("status", "unknown")

                print(f"\nTesting results for Job {job_id} (status: {status}):")

                # Try results endpoint
                try:
                    response = requests.get(
                        f"http://localhost:8000/api/jobs/{job_id}/results",
                        headers=headers,
                    )
                    print(f"   Results endpoint: {response.status_code}")
                    if response.status_code == 200:
                        data = response.json()
                        if isinstance(data, dict) and "results" in data:
                            print(f"   Results count: {len(data['results'])}")
                        else:
                            print(
                                f"   Results format: {type(data)} - {str(data)[:100]}..."
                            )
                    else:
                        print(f"   Error: {response.text[:100]}...")
                except Exception as e:
                    print(f"   Exception: {e}")

                # Try job details endpoint
                try:
                    response = requests.get(
                        f"http://localhost:8000/api/jobs/{job_id}", headers=headers
                    )
                    print(f"   Details endpoint: {response.status_code}")
                    if response.status_code == 200:
                        details = response.json()
                        print(
                            f"   Details keys: {list(details.keys()) if isinstance(details, dict) else 'Not dict'}"
                        )
                    else:
                        print(f"   Error: {response.text[:100]}...")
                except Exception as e:
                    print(f"   Exception: {e}")

    except Exception as e:
        print(f"❌ Error in results testing: {e}")


if __name__ == "__main__":
    print("🐛 Job Details & Results Debugging")
    print("=" * 50)

    # Test server connectivity
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is accessible")
        else:
            print(f"⚠️  Server responded with: {response.status_code}")
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        exit(1)

    # Run tests
    success = test_job_lifecycle()
    test_database_inspection()
    test_results_endpoints()

    print("\n" + "=" * 50)
    print("📊 DEBUGGING SUMMARY")
    print("=" * 50)

    if success:
        print("✅ Job lifecycle test passed")
        print("🔍 Check the detailed output above for any issues with:")
        print("   - Job details retrieval")
        print("   - Job execution status")
        print("   - Results availability")
    else:
        print("❌ Job lifecycle test failed")
        print("🔍 Issues found - check the error messages above")

    print("\n💡 Common issues:")
    print("   - Jobs not actually running/completing")
    print("   - Missing results in database")
    print("   - Frontend not calling correct endpoints")
    print("   - Authentication issues")
    print("=" * 50)
