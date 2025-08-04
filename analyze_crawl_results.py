#!/usr/bin/env python3
"""
Analyze crawling job results to understand why only one page was returned
"""

import json
import sqlite3
from datetime import datetime


def analyze_job_results():
    """Analyze job results from the database"""

    DATABASE_PATH = "/home/homebrew/scraper/data/scraper.db"

    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        print("🔍 Analyzing Recent Crawling Jobs")
        print("=" * 50)

        # Get recent jobs
        cursor.execute(
            """
            SELECT id, name, type, status, created_at, config, results_count
            FROM jobs 
            ORDER BY created_at DESC 
            LIMIT 10
        """
        )

        jobs = cursor.fetchall()

        print(f"📋 Found {len(jobs)} recent jobs:")
        for job in jobs:
            job_id, name, job_type, status, created_at, config, results_count = job

            # Extract URL from config
            url = "N/A"
            if config:
                try:
                    config_data = json.loads(config)
                    url = config_data.get("url", "N/A")
                except:
                    pass

            print(f"\n🔹 Job #{job_id}: {name}")
            print(f"   Type: {job_type}")
            print(f"   URL: {url}")
            print(f"   Status: {status}")
            print(f"   Results Count: {results_count}")
            print(f"   Created: {created_at}")

            if config:
                try:
                    config_data = json.loads(config)
                    print(f"   Config: {json.dumps(config_data, indent=6)}")
                except:
                    print(f"   Config: {config}")

            # Get job results
            cursor.execute(
                """
                SELECT data FROM job_results WHERE job_id = ? LIMIT 1
            """,
                (job_id,),
            )

            result = cursor.fetchone()
            if result:
                try:
                    result_data = json.loads(result[0])

                    print(f"   📊 Results Analysis:")
                    if isinstance(result_data, dict):
                        # Check if it's intelligent crawling result
                        if "summary" in result_data:
                            summary = result_data["summary"]
                            print(
                                f"      Pages processed: {summary.get('pages_processed', 0)}"
                            )
                            print(
                                f"      URLs discovered: {summary.get('urls_discovered', 0)}"
                            )
                            print(
                                f"      Data extracted: {summary.get('data_extracted', 0)}"
                            )

                            crawled_data = result_data.get("crawled_data", [])
                            print(f"      Crawled data items: {len(crawled_data)}")

                            if crawled_data:
                                print(
                                    f"      First page URL: {crawled_data[0].get('url', 'N/A')}"
                                )
                                if len(crawled_data) > 1:
                                    print(
                                        f"      Second page URL: {crawled_data[1].get('url', 'N/A')}"
                                    )
                                    print(
                                        f"      Last page URL: {crawled_data[-1].get('url', 'N/A')}"
                                    )
                        else:
                            # Single page result
                            print(
                                f"      Single page result for: {result_data.get('url', 'N/A')}"
                            )
                            print(f"      Status: {result_data.get('status', 'N/A')}")
                            links = result_data.get("links", [])
                            print(f"      Links found: {len(links)}")

                except Exception as e:
                    print(f"      Error parsing results: {e}")
            else:
                print(f"      No results found")

        # Find jobs that might be Thailand-related
        print(f"\n🇹🇭 Looking for Thailand crawling jobs...")
        cursor.execute(
            """
            SELECT id, name, type, status, config, results_count
            FROM jobs 
            WHERE config LIKE '%thailand%' OR config LIKE '%wikipedia%' OR name LIKE '%thailand%'
            ORDER BY created_at DESC 
            LIMIT 5
        """
        )

        thailand_jobs = cursor.fetchall()

        if thailand_jobs:
            print(f"Found {len(thailand_jobs)} Thailand-related jobs:")

            for job in thailand_jobs:
                job_id, name, job_type, status, config, results_count = job

                # Extract URL from config
                url = "N/A"
                if config:
                    try:
                        config_data = json.loads(config)
                        url = config_data.get("url", "N/A")
                    except:
                        pass

                print(f"\n🔹 Thailand Job #{job_id}: {name}")
                print(f"   Type: {job_type}")
                print(f"   URL: {url}")
                print(f"   Status: {status}")
                print(f"   Results Count: {results_count}")

                if config:
                    try:
                        config_data = json.loads(config)
                        max_depth = config_data.get("max_depth", "Not set")
                        max_pages = config_data.get("max_pages", "Not set")
                        print(f"   Max Depth: {max_depth}")
                        print(f"   Max Pages: {max_pages}")
                    except:
                        print(f"   Config: {config}")

                # Get detailed results for this job
                cursor.execute(
                    """
                    SELECT data FROM job_results WHERE job_id = ? LIMIT 1
                """,
                    (job_id,),
                )

                result = cursor.fetchone()
                if result:
                    try:
                        result_data = json.loads(result[0])

                        if (
                            isinstance(result_data, dict)
                            and "crawled_data" in result_data
                        ):
                            crawled_data = result_data["crawled_data"]
                            print(f"   📄 Actual crawled pages: {len(crawled_data)}")

                            # Show URLs of crawled pages
                            for i, page in enumerate(crawled_data[:5]):
                                page_url = page.get("url", "No URL")
                                page_title = page.get("title", "No title")[:50]
                                print(f"      Page {i+1}: {page_url}")
                                print(f"                {page_title}")

                                # Show link count for each page
                                links = page.get("links", [])
                                print(f"                Links found: {len(links)}")

                            if len(crawled_data) > 5:
                                print(
                                    f"      ... and {len(crawled_data) - 5} more pages"
                                )

                        elif isinstance(result_data, dict):
                            # Single page result
                            print(f"   📄 Single page result:")
                            print(f"      URL: {result_data.get('url', 'N/A')}")
                            print(
                                f"      Title: {result_data.get('title', 'N/A')[:50]}"
                            )
                            links = result_data.get("links", [])
                            print(f"      Links found: {len(links)}")

                    except Exception as e:
                        print(f"      Error analyzing results: {e}")
        else:
            print("No Thailand-related jobs found.")

        conn.close()

    except Exception as e:
        print(f"❌ Database analysis failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    analyze_job_results()
