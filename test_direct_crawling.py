#!/usr/bin/env python3
"""
Direct test of the fixed intelligent crawling functionality
"""

import asyncio
import json
import sqlite3
from datetime import datetime
from scraping_engine import execute_scraping_job

async def test_fixed_intelligent_crawling():
    """Test the fixed intelligent crawling directly"""
    
    print("🔧 Testing Fixed Intelligent Crawling Engine")
    print("=" * 60)
    
    # Create test job configuration with the fixed structure
    job_config = {
        "url": "https://en.wikipedia.org/wiki/Thailand",
        "type": "intelligent_crawling",  # This is now included!
        "scraper_type": "intelligent",
        "max_depth": 3,
        "max_pages": 15,
        "follow_internal_links": True,
        "follow_external_links": False,
        "rate_limit": {
            "requests_per_second": 1.5
        },
        "config": {
            "custom_selectors": {}
        }
    }
    
    print("📋 Job Configuration:")
    print(json.dumps(job_config, indent=2))
    
    # Create a test job in the database
    DATABASE_PATH = "/home/homebrew/scraper/data/scraper.db"
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Create job entry
        cursor.execute("""
            INSERT INTO jobs (name, type, status, config, created_by)
            VALUES (?, ?, ?, ?, ?)
        """, (
            "Direct Test - Thailand Intelligent Crawl",
            "intelligent_crawling",
            "pending",
            json.dumps(job_config),
            1
        ))
        
        job_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"\n✅ Created test job #{job_id}")
        
        # Execute the job using the fixed function
        print(f"\n🚀 Executing job with fixed engine...")
        start_time = datetime.now()
        
        result = await execute_scraping_job(job_id, job_config)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n📊 Execution Results (Duration: {duration:.2f}s):")
        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   Job ID: {result.get('job_id', 'N/A')}")
        print(f"   URL: {result.get('url', 'N/A')}")
        
        # Analyze the detailed results
        data = result.get('data', {})
        print(f"\n🔍 Data Analysis:")
        print(f"   Data type: {type(data)}")
        
        if isinstance(data, dict):
            if 'summary' in data:
                # This should be intelligent crawling results
                print(f"   ✅ INTELLIGENT CRAWLING DETECTED!")
                summary = data['summary']
                print(f"   📈 Summary:")
                print(f"      Pages processed: {summary.get('pages_processed', 0)}")
                print(f"      URLs discovered: {summary.get('urls_discovered', 0)}")
                print(f"      Data extracted: {summary.get('data_extracted', 0)}")
                print(f"      URLs queued: {summary.get('urls_queued', 0)}")
                
                crawled_data = data.get('crawled_data', [])
                print(f"   📄 Crawled Data: {len(crawled_data)} pages")
                
                if len(crawled_data) > 1:
                    print(f"   🎯 SUCCESS: Multiple pages crawled!")
                    print(f"   📑 Sample Pages:")
                    for i, page in enumerate(crawled_data[:5]):
                        url = page.get('url', 'No URL')
                        title = page.get('title', 'No title')[:50]
                        links_count = len(page.get('links', []))
                        print(f"      {i+1}. {url}")
                        print(f"         Title: {title}")
                        print(f"         Links: {links_count}")
                    
                    if len(crawled_data) > 5:
                        print(f"      ... and {len(crawled_data) - 5} more pages")
                
                discovered_urls = data.get('discovered_urls', [])
                print(f"   🔗 Discovered URLs: {len(discovered_urls)}")
                if discovered_urls:
                    print(f"      Sample discovered URLs:")
                    for i, url in enumerate(discovered_urls[:5]):
                        print(f"         {i+1}. {url}")
                    if len(discovered_urls) > 5:
                        print(f"         ... and {len(discovered_urls) - 5} more")
                
                errors = data.get('errors', [])
                if errors:
                    print(f"   ⚠️  Errors: {len(errors)}")
                    for error in errors[:3]:
                        print(f"      - {error}")
                
            else:
                # Single page result
                print(f"   ❌ SINGLE PAGE RESULT (crawling did not work)")
                print(f"      URL: {data.get('url', 'N/A')}")
                print(f"      Title: {data.get('title', 'N/A')}")
                print(f"      Status: {data.get('status', 'N/A')}")
                links = data.get('links', [])
                print(f"      Links found: {len(links)}")
                
        # Verify the job in the database
        print(f"\n🗄️  Database Verification:")
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT status, results_count FROM jobs WHERE id = ?
        """, (job_id,))
        
        job_status = cursor.fetchone()
        if job_status:
            status, results_count = job_status
            print(f"   Job status: {status}")
            print(f"   Results count: {results_count}")
        
        cursor.execute("""
            SELECT data FROM job_results WHERE job_id = ?
        """, (job_id,))
        
        stored_result = cursor.fetchone()
        if stored_result:
            stored_data = json.loads(stored_result[0])
            if 'summary' in stored_data:
                stored_summary = stored_data['summary']
                print(f"   Stored pages processed: {stored_summary.get('pages_processed', 0)}")
            else:
                print(f"   Stored single page result")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fixed_intelligent_crawling())
