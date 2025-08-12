#!/usr/bin/env python3
"""
Test script to verify the backend API and debug modal issues
"""

import json
import time

import requests


def test_backend_api():
    """Test the backend API endpoints"""
    base_url = "http://localhost:8000"

    print("🧪 Testing Backend API...")

    # Test health check
    try:
        response = requests.get(f"{base_url}/api/health")
        print(f"✅ Health check: {response.status_code} - {response.text[:100]}...")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

    # Test AI service status
    try:
        print("\n🤖 Testing AI Service Status...")
        ai_status_response = requests.get(f"{base_url}/api/ai/service/status")
        print(f"AI Service status: {ai_status_response.status_code}")

        if ai_status_response.status_code == 200:
            ai_status = ai_status_response.json()
            print(
                f"   AI Service available: {ai_status.get('ai_service_available', False)}"
            )
            if ai_status.get("capabilities"):
                capabilities = ai_status["capabilities"]
                print(
                    f"   Content clustering: {capabilities.get('content_clustering', False)}"
                )
                print(
                    f"   Predictive analytics: {capabilities.get('predictive_analytics', False)}"
                )
                print(
                    f"   Real-time monitoring: {capabilities.get('real_time_monitoring', False)}"
                )
        else:
            print(
                f"❌ AI Service status check failed: {ai_status_response.status_code}"
            )

    except Exception as e:
        print(f"❌ AI Service status check error: {e}")

    # Login to get token
    try:
        login_data = {"username": "admin", "password": "admin123"}

        print("\n🔐 Logging in...")
        login_response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        print(f"Login response: {login_response.status_code}")

        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data.get("access_token")
            print(f"✅ Login successful, got token")

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            return False

    except Exception as e:
        print(f"❌ Login failed: {e}")
        return False

    # Create a test job
    try:
        job_data = {
            "name": "Debug Test Job",
            "type": "web_scraping",
            "url": "https://en.wikipedia.org/wiki/Python_(programming_language)",
            "scraper_type": "basic",
            "config": {
                "crawl_links": True,
                "max_links": 3,
                "include_images": True,
                "max_pages": 5000,
            },
        }

        print("\n🚀 Creating test job...")
        response = requests.post(f"{base_url}/api/jobs", json=job_data, headers=headers)
        print(f"Create job response: {response.status_code}")

        if response.status_code == 200 or response.status_code == 201:
            job_response = response.json()
            print(f"   Job response: {job_response}")
            job_id = job_response.get("job_id") or job_response.get("id")
            print(f"✅ Job created with ID: {job_id}")

            # Start the job
            print(f"\n🎯 Starting job {job_id}...")
            start_response = requests.post(
                f"{base_url}/api/jobs/{job_id}/start", headers=headers
            )
            print(f"Start job response: {start_response.status_code}")

            # Wait a bit for job to process
            print("\n⏳ Waiting for job to process...")
            time.sleep(15)

            # Get job results
            print(f"\n📊 Getting results for job {job_id}...")
            results_response = requests.get(
                f"{base_url}/api/jobs/{job_id}/results", headers=headers
            )
            print(f"Results response status: {results_response.status_code}")

            if results_response.status_code == 200:
                results = results_response.json()
                print(f"✅ Results received!")
                print(f"   Data structure: {type(results)}")

                if isinstance(results, list) and len(results) > 0:
                    first_item = results[0]
                    print(f"   First item type: {type(first_item)}")
                    print(
                        f"   First item keys: {list(first_item.keys()) if isinstance(first_item, dict) else 'Not a dict'}"
                    )

                    if isinstance(first_item, dict) and "crawled_data" in first_item:
                        crawled_data = first_item["crawled_data"]
                        print(
                            f"   Crawled data length: {len(crawled_data) if isinstance(crawled_data, list) else 'Not a list'}"
                        )

                        if isinstance(crawled_data, list) and len(crawled_data) > 0:
                            sample_item = crawled_data[0]
                            print(
                                f"   Sample item keys: {list(sample_item.keys()) if isinstance(sample_item, dict) else 'Not a dict'}"
                            )

                            # Test Phase 4 AI Analysis
                            print(f"\n🤖 Testing Phase 4 AI Analysis...")
                            ai_test_data = {
                                "data": crawled_data[
                                    :5
                                ],  # Use first 5 items for testing
                                "analysis_type": "full",
                                "options": {"include_visualizations": True},
                            }

                            ai_response = requests.post(
                                f"{base_url}/api/ai/analyze",
                                json=ai_test_data,
                                headers=headers,
                            )
                            print(f"AI Analysis response: {ai_response.status_code}")

                            if ai_response.status_code == 200:
                                ai_result = ai_response.json()
                                print(f"✅ AI Analysis successful!")
                                print(
                                    f"   Analysis ID: {ai_result.get('analysis_id', 'N/A')}"
                                )
                                print(
                                    f"   Processing time: {ai_result.get('processing_time', 'N/A')}s"
                                )
                                print(
                                    f"   Recommendations: {len(ai_result.get('recommendations', []))}"
                                )
                                print(
                                    f"   Insights available: {bool(ai_result.get('insights'))}"
                                )
                                print(
                                    f"   Visualizations: {bool(ai_result.get('visualizations'))}"
                                )
                            else:
                                print(
                                    f"❌ AI Analysis failed: {ai_response.status_code}"
                                )
                                print(f"   Response: {ai_response.text}")

                            # Test Real-time Dashboard
                            print(f"\n📊 Testing Real-time AI Dashboard...")
                            dashboard_response = requests.get(
                                f"{base_url}/api/ai/realtime-dashboard", headers=headers
                            )
                            print(
                                f"Dashboard response: {dashboard_response.status_code}"
                            )

                            if dashboard_response.status_code == 200:
                                dashboard_data = dashboard_response.json()
                                print(f"✅ Real-time dashboard working!")
                                print(
                                    f"   AI service stats: {bool(dashboard_data.get('ai_service_stats'))}"
                                )
                                print(
                                    f"   Dashboard data: {bool(dashboard_data.get('dashboard'))}"
                                )
                            else:
                                print(
                                    f"❌ Dashboard failed: {dashboard_response.status_code}"
                                )

                return True
            else:
                print(f"❌ Failed to get results: {results_response.status_code}")
                print(f"   Response: {results_response.text}")

        else:
            print(f"❌ Failed to create job: {response.status_code}")
            print(f"   Response: {response.text}")

    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

    return False


if __name__ == "__main__":
    print("🔧 Backend API Debug Test")
    print("=" * 50)

    success = test_backend_api()

    if success:
        print("\n✅ Backend API is working correctly!")
        print("\n💡 Next steps:")
        print("   1. Open http://localhost:5177 in your browser")
        print("   2. Open Developer Console (F12)")
        print("   3. Create a scraping job")
        print("   4. Click 'Show Collected Data' button")
        print("   5. Look for debug messages with 🚨 emoji")
    else:
        print("\n❌ Backend API test failed!")
