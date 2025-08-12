#!/usr/bin/env python3
"""
Test script to verify the max_pages fix works correctly
"""

import json
import time

import requests


def test_max_pages_fix():
    """Test that max_pages configuration is properly preserved"""
    base_url = "http://localhost:8000"

    print("🧪 Testing max_pages configuration fix...")

    # Login to get token
    try:
        login_data = {"username": "admin", "password": "admin123"}

        print("\n🔐 Logging in...")
        login_response = requests.post(f"{base_url}/api/auth/login", json=login_data)

        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data.get("access_token")
            print(f"✅ Login successful")

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Login failed: {e}")
        return False

    # Test different max_pages values
    test_cases = [
        {"max_pages": 100, "expected": 100},
        {"max_pages": 500, "expected": 500},
        {"max_pages": 2000, "expected": 2000},
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🎯 Test Case {i}: max_pages = {test_case['max_pages']}")

        # Create a test job with specific max_pages
        job_data = {
            "name": f"Max Pages Test {i}",
            "type": "web_scraping",
            "url": "https://en.wikipedia.org/wiki/Python_(programming_language)",
            "scraper_type": "basic",
            "config": {
                "crawl_links": True,
                "max_links": 10,
                "include_images": True,
                "max_pages": test_case["max_pages"],
                "max_depth": 2,
            },
        }

        try:
            print(f"   🚀 Creating job with max_pages={test_case['max_pages']}...")
            response = requests.post(
                f"{base_url}/api/jobs", json=job_data, headers=headers
            )

            if response.status_code in [200, 201]:
                job_response = response.json()
                job_id = job_response.get("job_id") or job_response.get("id")
                print(f"   ✅ Job created with ID: {job_id}")

                # Get the job details to verify config was saved correctly
                print(f"   🔍 Checking job configuration...")
                job_details_response = requests.get(
                    f"{base_url}/api/jobs/{job_id}", headers=headers
                )

                if job_details_response.status_code == 200:
                    job_details = job_details_response.json()

                    # Extract the stored config
                    stored_config = job_details.get("config", {})
                    if isinstance(stored_config, str):
                        stored_config = json.loads(stored_config)

                    # Check if max_pages was preserved
                    config_section = stored_config.get("config", {})
                    stored_max_pages = config_section.get("max_pages")

                    print(
                        f"   📋 Stored config: {json.dumps(config_section, indent=2)}"
                    )
                    print(f"   🎯 Expected max_pages: {test_case['expected']}")
                    print(f"   💾 Stored max_pages: {stored_max_pages}")

                    if stored_max_pages == test_case["expected"]:
                        print(f"   ✅ SUCCESS: max_pages correctly preserved!")
                    else:
                        print(f"   ❌ FAILED: max_pages not preserved correctly")
                        print(f"      Expected: {test_case['expected']}")
                        print(f"      Got: {stored_max_pages}")
                        return False
                else:
                    print(
                        f"   ❌ Failed to get job details: {job_details_response.status_code}"
                    )
                    return False

            else:
                print(f"   ❌ Failed to create job: {response.status_code}")
                print(f"   Response: {response.text}")
                return False

        except Exception as e:
            print(f"   ❌ Test case {i} failed: {e}")
            return False

    print(
        f"\n🎉 All test cases passed! max_pages configuration is now working correctly."
    )
    print(
        f"\n💡 Now when you create jobs with high max_pages values, they should be preserved."
    )
    print(f"   Instead of defaulting to 50, your jobs will use the configured value.")

    return True


if __name__ == "__main__":
    print("🔧 Max Pages Configuration Fix Test")
    print("=" * 50)

    success = test_max_pages_fix()

    if success:
        print("\n✅ Fix verified successfully!")
        print("\nYour max_pages configuration should now work properly.")
        print(
            "Try creating a new job with max_pages > 50 and it should crawl more pages."
        )
    else:
        print("\n❌ Fix verification failed!")
        print("The max_pages configuration is still not working correctly.")
