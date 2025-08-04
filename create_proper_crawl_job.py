#!/usr/bin/env python3
"""
Create a proper intelligent crawling job for Thailand with depth configuration
"""

import asyncio
import json
import sqlite3
from datetime import datetime

from scraping_engine import execute_scraping_job


def create_thailand_crawling_job():
    """Create a properly configured Thailand crawling job"""

    DATABASE_PATH = "/home/homebrew/scraper/data/scraper.db"

    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Create a proper intelligent crawling job
        job_config = {
            "url": "https://en.wikipedia.org/wiki/Thailand",
            "scraper_type": "intelligent",
            "max_depth": 3,
            "max_pages": 15,
            "follow_internal_links": True,
            "follow_external_links": False,
            "rate_limit": {"requests_per_second": 1.0},
        }

        cursor.execute(
            """
            INSERT INTO jobs (name, type, status, config, created_by)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                "Thailand Intelligent Crawl - Depth 3",
                "intelligent_crawling",  # This is the key difference!
                "pending",
                json.dumps(job_config),
                1,  # Admin user
            ),
        )

        job_id = cursor.lastrowid
        conn.commit()
        conn.close()

        print(f"✅ Created intelligent crawling job #{job_id}")
        print(f"   Name: Thailand Intelligent Crawl - Depth 3")
        print(f"   Type: intelligent_crawling")
        print(f"   URL: {job_config['url']}")
        print(f"   Max Depth: {job_config['max_depth']}")
        print(f"   Max Pages: {job_config['max_pages']}")

        return job_id, job_config

    except Exception as e:
        print(f"❌ Failed to create job: {e}")
        return None, None


async def execute_thailand_crawling():
    """Execute the Thailand crawling job"""

    print("🕷️ Creating and Executing Thailand Intelligent Crawling Job")
    print("=" * 60)

    # Create the job
    job_id, job_config = create_thailand_crawling_job()

    if job_id:
        print(f"\n🚀 Executing job #{job_id}...")

        try:
            # Execute the job
            result = await execute_scraping_job(job_id, job_config)

            print(f"\n📊 Job Execution Results:")
            print(f"   Status: {result.get('status', 'unknown')}")
            print(f"   Job ID: {result.get('job_id', 'N/A')}")
            print(f"   URL: {result.get('url', 'N/A')}")

            # Analyze the detailed results
            data = result.get("data", {})
            if isinstance(data, dict):
                if "summary" in data:
                    # Intelligent crawling result
                    summary = data["summary"]
                    print(f"   Pages processed: {summary.get('pages_processed', 0)}")
                    print(f"   URLs discovered: {summary.get('urls_discovered', 0)}")
                    print(f"   Data extracted: {summary.get('data_extracted', 0)}")

                    crawled_data = data.get("crawled_data", [])
                    print(f"   Crawled pages: {len(crawled_data)}")

                    if crawled_data:
                        print(f"\n🔗 Crawled Pages:")
                        for i, page in enumerate(crawled_data[:5]):
                            page_url = page.get("url", "No URL")
                            page_title = page.get("title", "No title")[:50]
                            links_count = len(page.get("links", []))
                            print(f"   {i+1}. {page_url}")
                            print(f"      Title: {page_title}")
                            print(f"      Links found: {links_count}")

                        if len(crawled_data) > 5:
                            print(f"   ... and {len(crawled_data) - 5} more pages")

                    discovered_urls = data.get("discovered_urls", [])
                    if discovered_urls:
                        print(f"\n🌐 Sample Discovered URLs:")
                        for i, url in enumerate(discovered_urls[:10]):
                            print(f"   {i+1}. {url}")
                        if len(discovered_urls) > 10:
                            print(f"   ... and {len(discovered_urls) - 10} more")

                else:
                    # Single page result
                    print(f"   ⚠️  Got single page result instead of crawling result")
                    print(f"   Page URL: {data.get('url', 'N/A')}")
                    print(f"   Page title: {data.get('title', 'N/A')}")
                    links = data.get("links", [])
                    print(f"   Links found: {len(links)}")

        except Exception as e:
            print(f"❌ Job execution failed: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(execute_thailand_crawling())
