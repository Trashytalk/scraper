#!/usr/bin/env python3
"""
Test script to verify the complete intelligent crawling workflow
including frontend job creation and results retrieval
"""

import asyncio
import sqlite3
import json
from datetime import datetime
from scraping_engine import execute_scraping_job

async def test_complete_crawling_workflow():
    """Test the complete crawling workflow from job creation to results"""
    
    print("🔧 Testing Complete Intelligent Crawling Workflow")
    print("=" * 60)
    
    DATABASE_PATH = "/home/homebrew/scraper/data/scraper.db"
    
    # Test different crawling configurations
    test_cases = [
        {
            "name": "Wikipedia Thailand - Depth 2",
            "config": {
                "url": "https://en.wikipedia.org/wiki/Thailand",
                "type": "intelligent_crawling",
                "scraper_type": "intelligent",
                "max_depth": 2,
                "max_pages": 8,
                "follow_internal_links": True,
                "follow_external_links": False,
                "rate_limit": {
                    "requests_per_second": 2.0
                }
            }
        },
        {
            "name": "Wikipedia Thailand - Depth 3", 
            "config": {
                "url": "https://en.wikipedia.org/wiki/Thailand",
                "type": "intelligent_crawling",
                "scraper_type": "intelligent", 
                "max_depth": 3,
                "max_pages": 12,
                "follow_internal_links": True,
                "follow_external_links": False,
                "rate_limit": {
                    "requests_per_second": 1.5
                }
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['name']}")
        print("-" * 40)
        
        config = test_case['config']
        print(f"Max Depth: {config['max_depth']}")
        print(f"Max Pages: {config['max_pages']}")
        print(f"URL: {config['url']}")
        
        try:
            # Create job in database (simulating frontend)
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO jobs (name, type, status, config, created_by)
                VALUES (?, ?, ?, ?, ?)
            """, (
                test_case['name'],
                "intelligent_crawling",
                "pending", 
                json.dumps(config),
                1
            ))
            
            job_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            print(f"✅ Created job #{job_id}")
            
            # Execute job
            start_time = datetime.now()
            result = await execute_scraping_job(job_id, config)
            end_time = datetime.now()
            
            duration = (end_time - start_time).total_seconds()
            print(f"⏱️  Execution time: {duration:.2f} seconds")
            
            # Analyze results
            data = result.get('data', {})
            if isinstance(data, dict) and 'summary' in data:
                summary = data['summary']
                crawled_data = data.get('crawled_data', [])
                discovered_urls = data.get('discovered_urls', [])
                
                print(f"📊 Results:")
                print(f"   Status: {result.get('status', 'unknown')}")
                print(f"   Pages processed: {summary.get('pages_processed', 0)}")
                print(f"   URLs discovered: {summary.get('urls_discovered', 0)}")
                print(f"   Data extracted: {summary.get('data_extracted', 0)}")
                print(f"   Crawled data items: {len(crawled_data)}")
                
                # Verify depth was respected
                expected_min_pages = min(config['max_depth'], config['max_pages'])
                actual_pages = len(crawled_data)
                
                if actual_pages >= expected_min_pages and actual_pages > 1:
                    print(f"✅ SUCCESS: Crawled {actual_pages} pages (expected >= {expected_min_pages})")
                    
                    # Show sample crawled pages
                    print(f"📄 Sample crawled pages:")
                    for j, page in enumerate(crawled_data[:3]):
                        url = page.get('url', 'No URL')
                        title = page.get('title', 'No title')[:50]
                        links_count = len(page.get('links', []))
                        print(f"   {j+1}. {url}")
                        print(f"      Title: {title}")
                        print(f"      Links: {links_count}")
                        
                    if len(crawled_data) > 3:
                        print(f"   ... and {len(crawled_data) - 3} more pages")
                        
                else:
                    print(f"❌ FAILED: Only crawled {actual_pages} pages, expected at least {expected_min_pages}")
                    
                # Show discovered URLs
                if discovered_urls:
                    print(f"🔗 Sample discovered URLs:")
                    for j, url in enumerate(discovered_urls[:5]):
                        print(f"   {j+1}. {url}")
                    if len(discovered_urls) > 5:
                        print(f"   ... and {len(discovered_urls) - 5} more")
                        
                # Verify database storage
                conn = sqlite3.connect(DATABASE_PATH)
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT status, results_count FROM jobs WHERE id = ?
                """, (job_id,))
                
                job_status = cursor.fetchone()
                if job_status:
                    status, results_count = job_status
                    print(f"💾 Database: Status={status}, Results={results_count}")
                    
                    if results_count == actual_pages:
                        print("✅ Database results count matches crawled data")
                    else:
                        print(f"⚠️  Database results count ({results_count}) != crawled data ({actual_pages})")
                
                conn.close()
                
            else:
                print(f"❌ FAILED: Got single page result instead of crawling")
                print(f"   Data type: {type(data)}")
                if isinstance(data, dict):
                    print(f"   Keys: {list(data.keys())}")
                    
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            
        print() # Empty line between tests
    
    # Summary
    print("=" * 60)
    print("🏁 Workflow Test Complete!")
    print("\n💡 Next Steps:")
    print("1. Start the frontend: cd business_intel_scraper/frontend && npm run dev")
    print("2. Restart backend with dependencies: pip install fastapi uvicorn")
    print("3. Create jobs using 'Intelligent Crawling' mode in the frontend")
    print("4. Set max_depth to 2 or 3 for multi-page crawling")

if __name__ == "__main__":
    asyncio.run(test_complete_crawling_workflow())
