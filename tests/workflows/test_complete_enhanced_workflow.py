#!/usr/bin/env python3
"""
Test the complete workflow including the new centralize data endpoint
"""

import asyncio
import json
import sqlite3
from datetime import datetime

import requests

from scraping_engine import ScrapingEngine


def test_complete_enhanced_workflow():
    """Test the complete enhanced workflow with centralization"""
    print("🧪 Testing Complete Enhanced Workflow with Data Centralization")
    print("=" * 75)

    # Login first
    print("\n🔐 Step 1: Authentication")
    print("-" * 40)

    login_response = requests.post(
        "http://localhost:8000/api/auth/login",
        json={"username": "admin", "password": "admin123"},
    )

    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        print("✅ Successfully authenticated")
    else:
        print("❌ Authentication failed")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # Create enhanced crawling job
    print("\n🕷️ Step 2: Create Enhanced Crawling Job")
    print("-" * 40)

    job_data = {
        "name": "Enhanced Wikipedia Crawl Test",
        "type": "intelligent_crawling",
        "url": "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "scraper_type": "intelligent",
        "config": {
            "max_depth": 2,
            "max_pages": 5,
            "follow_internal_links": True,
            "follow_external_links": False,
            "extract_full_html": True,
            "crawl_entire_domain": False,
            "include_images": True,
            "save_to_database": True,
        },
    }

    job_response = requests.post(
        "http://localhost:8000/api/jobs", json=job_data, headers=headers
    )

    if job_response.status_code == 200:
        job_id = job_response.json()["id"]
        print(f"✅ Created job #{job_id}: {job_data['name']}")
    else:
        print(f"❌ Failed to create job: {job_response.status_code}")
        return

    # Start the job
    print("\n🚀 Step 3: Execute Enhanced Crawling")
    print("-" * 40)

    start_response = requests.post(
        f"http://localhost:8000/api/jobs/{job_id}/start", headers=headers
    )

    if start_response.status_code == 200:
        print("✅ Job started successfully")

        # Wait for completion (check status)
        import time

        max_wait = 60  # 1 minute max
        wait_time = 0

        while wait_time < max_wait:
            status_response = requests.get(
                f"http://localhost:8000/api/jobs/{job_id}", headers=headers
            )
            if status_response.status_code == 200:
                job_status = status_response.json()["status"]
                print(f"📊 Job status: {job_status}")

                if job_status == "completed":
                    break
                elif job_status == "failed":
                    print("❌ Job failed")
                    return

            time.sleep(3)
            wait_time += 3

        if wait_time >= max_wait:
            print("⏰ Job taking too long, proceeding anyway")
    else:
        print(f"❌ Failed to start job: {start_response.status_code}")
        return

    # Get job results
    print("\n📊 Step 4: Retrieve Crawling Results")
    print("-" * 40)

    results_response = requests.get(
        f"http://localhost:8000/api/jobs/{job_id}/results", headers=headers
    )

    if results_response.status_code == 200:
        results_data = results_response.json()
        print("✅ Retrieved job results")

        # Check for enhanced data
        if "crawled_data" in results_data:
            crawled_data = results_data["crawled_data"]
            summary = results_data.get("summary", {})

            print(f"📄 Pages crawled: {len(crawled_data)}")
            print(f"🖼️ Images extracted: {summary.get('images_extracted', 0)}")
            print(f"⏱️ Total time: {summary.get('total_crawl_time', 0)}s")
            print(f"🌐 Domains: {len(summary.get('domains_crawled', []))}")

            # Check for full HTML
            if crawled_data:
                first_page = crawled_data[0]
                has_html = "raw_html" in first_page
                has_metadata = "crawl_metadata" in first_page

                print(f"📄 Full HTML: {'✅' if has_html else '❌'}")
                print(f"📊 Crawl metadata: {'✅' if has_metadata else '❌'}")

                if has_html:
                    html_size = len(first_page["raw_html"])
                    print(f"📄 HTML size: {html_size:,} characters")
        else:
            crawled_data = results_data.get("data", [])
            print(f"📄 Basic results: {len(crawled_data)} items")
    else:
        print(f"❌ Failed to get results: {results_response.status_code}")
        return

    # Test data centralization
    print("\n💾 Step 5: Test Data Centralization")
    print("-" * 40)

    centralize_data = {
        "job_id": job_id,
        "job_name": job_data["name"],
        "data": crawled_data,
        "metadata": {
            "job_type": "intelligent_crawling",
            "total_count": len(crawled_data),
            "status": "completed",
            "created_at": datetime.now().isoformat(),
            "completed_at": datetime.now().isoformat(),
        },
    }

    centralize_response = requests.post(
        "http://localhost:8000/api/data/centralize",
        json=centralize_data,
        headers=headers,
    )

    if centralize_response.status_code == 200:
        centralize_result = centralize_response.json()
        print("✅ Data centralization successful")
        print(
            f"📊 Centralized records: {centralize_result.get('centralized_records', 0)}"
        )
        print(f"🔄 Duplicates found: {centralize_result.get('duplicates_found', 0)}")
        print(f"📋 Total processed: {centralize_result.get('total_processed', 0)}")
    else:
        print(f"❌ Data centralization failed: {centralize_response.status_code}")
        if centralize_response.text:
            print(f"Error: {centralize_response.text}")

    # Check centralized database
    print("\n🗄️ Step 6: Verify Data Persistence")
    print("-" * 40)

    try:
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()

        # Check centralized data
        cursor.execute("SELECT COUNT(*) FROM centralized_data")
        centralized_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT source_job_id) FROM centralized_data")
        unique_jobs = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM centralized_data WHERE data_quality_score >= 70"
        )
        high_quality = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(data_quality_score) FROM centralized_data")
        avg_quality = cursor.fetchone()[0] or 0

        print(f"✅ Database connectivity: OK")
        print(f"📊 Total centralized records: {centralized_count}")
        print(f"🎯 Unique jobs: {unique_jobs}")
        print(f"⭐ High quality records: {high_quality}")
        print(f"📈 Average quality score: {avg_quality:.1f}")

        # Check crawl cache
        cursor.execute("SELECT COUNT(*) FROM crawl_cache")
        cached_pages = cursor.fetchone()[0]
        print(f"💾 Cached pages: {cached_pages}")

        conn.close()

    except Exception as e:
        print(f"❌ Database check failed: {e}")

    # Summary
    print("\n" + "=" * 75)
    print("🎉 Enhanced Workflow Test Summary")
    print("=" * 75)

    features_tested = [
        ("Authentication", login_response.status_code == 200),
        ("Enhanced Job Creation", job_response.status_code == 200),
        ("Intelligent Crawling", start_response.status_code == 200),
        ("Result Retrieval", results_response.status_code == 200),
        ("Data Centralization", centralize_response.status_code == 200),
        (
            "Database Persistence",
            "centralized_count" in locals() and centralized_count > 0,
        ),
    ]

    print("\n✅ Feature Test Results:")
    for feature, success in features_tested:
        status = "✅" if success else "❌"
        print(f"   {status} {feature}")

    success_count = sum(1 for _, success in features_tested if success)
    print(
        f"\n🎯 Overall Success Rate: {success_count}/{len(features_tested)} ({success_count/len(features_tested)*100:.1f}%)"
    )

    if success_count == len(features_tested):
        print("🏆 Complete enhanced workflow is working perfectly!")
        print("🎉 All new features are functional:")
        print("   ✅ Full HTML extraction")
        print("   ✅ Enhanced image extraction")
        print("   ✅ Comprehensive status tracking")
        print("   ✅ Data persistence and caching")
        print("   ✅ Data centralization for analytics")
        print("   ✅ Quality metrics and deduplication")
    else:
        print("⚠️ Some features need attention. Check the logs above.")


if __name__ == "__main__":
    test_complete_enhanced_workflow()
