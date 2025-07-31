#!/usr/bin/env python3
"""
Test script to verify intelligent crawling depth functionality
"""

import asyncio
import json
from scraping_engine import ScrapingEngine
from datetime import datetime

async def test_crawling_depth():
    """Test crawling with different depth configurations"""
    
    engine = ScrapingEngine()
    
    # Test configuration for different depths
    test_configs = [
        {
            "name": "Depth 1 (Seed page only)",
            "config": {
                "max_depth": 1,
                "max_pages": 10,
                "follow_internal_links": True,
                "follow_external_links": False
            }
        },
        {
            "name": "Depth 2 (Seed + direct links)",
            "config": {
                "max_depth": 2,
                "max_pages": 15,
                "follow_internal_links": True,
                "follow_external_links": False
            }
        },
        {
            "name": "Depth 3 (Three levels deep)",
            "config": {
                "max_depth": 3,
                "max_pages": 20,
                "follow_internal_links": True,
                "follow_external_links": False
            }
        }
    ]
    
    seed_url = "https://en.wikipedia.org/wiki/Thailand"
    
    print("🕷️ Testing Intelligent Crawling Depth Functionality")
    print("=" * 60)
    
    for test in test_configs:
        print(f"\n🔍 Testing: {test['name']}")
        print(f"Configuration: {json.dumps(test['config'], indent=2)}")
        print("-" * 40)
        
        try:
            start_time = datetime.now()
            
            # Run intelligent crawl with specific depth
            result = await engine.intelligent_crawl(
                seed_url, 
                scraper_type="basic", 
                config=test['config']
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Analyze results
            summary = result.get('summary', {})
            crawled_data = result.get('crawled_data', [])
            discovered_urls = result.get('discovered_urls', [])
            
            print(f"✅ Status: {result.get('status', 'unknown')}")
            print(f"⏱️  Duration: {duration:.2f} seconds")
            print(f"📄 Pages processed: {summary.get('pages_processed', 0)}")
            print(f"🔗 URLs discovered: {summary.get('urls_discovered', 0)}")
            print(f"📊 Data extracted: {summary.get('data_extracted', 0)}")
            
            # Show depth distribution
            depth_distribution = {}
            for page in crawled_data:
                url = page.get('url', '')
                # Try to determine depth by matching against discovered URLs
                if url == seed_url:
                    depth = 0
                else:
                    # For this test, we'll estimate depth
                    depth = 1  # Simplified for this test
                
                depth_distribution[depth] = depth_distribution.get(depth, 0) + 1
            
            print(f"🌳 Depth distribution: {depth_distribution}")
            
            # Show first few discovered URLs
            if discovered_urls:
                print("🔗 Sample discovered URLs:")
                for i, url in enumerate(discovered_urls[:5]):
                    print(f"   {i+1}. {url}")
                if len(discovered_urls) > 5:
                    print(f"   ... and {len(discovered_urls) - 5} more")
            
            # Show detailed results for verification
            print(f"\n📋 Detailed Analysis:")
            print(f"   Max depth configured: {test['config']['max_depth']}")
            print(f"   Max pages configured: {test['config']['max_pages']}")
            print(f"   Actual pages crawled: {len(crawled_data)}")
            print(f"   Follow internal links: {test['config']['follow_internal_links']}")
            print(f"   Follow external links: {test['config']['follow_external_links']}")
            
            # Verify crawling logic
            if len(crawled_data) == 1 and test['config']['max_depth'] > 1:
                print("⚠️  WARNING: Only 1 page crawled despite max_depth > 1")
                print("    This suggests the crawling depth logic may not be working correctly")
                
                # Show the single page data
                if crawled_data:
                    page = crawled_data[0]
                    links = page.get('links', [])
                    print(f"    Seed page has {len(links)} links available for crawling")
                    if len(links) > 0:
                        print("    Sample links from seed page:")
                        for i, link in enumerate(links[:3]):
                            if isinstance(link, dict):
                                print(f"      - {link.get('url', 'No URL')} ({link.get('text', 'No text')[:50]})")
                            else:
                                print(f"      - {link}")
            
            # Check for errors
            errors = result.get('errors', [])
            if errors:
                print(f"❌ Errors encountered: {len(errors)}")
                for error in errors[:3]:
                    print(f"   - {error}")
                    
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🏁 Crawling depth tests completed!")

if __name__ == "__main__":
    asyncio.run(test_crawling_depth())
