#!/usr/bin/env python3
"""
Debug script to test domain crawling functionality
"""

import asyncio
import json
from scraping_engine import ScrapingEngine


async def test_domain_crawl():
    """Test domain crawling with debug output"""
    engine = ScrapingEngine()
    
    # Test with a domain that has internal links
    url = "https://httpbin.org"
    
    # Configuration that should enable domain crawling
    config = {
        "max_pages": 10,
        "max_depth": 2,
        "crawl_entire_domain": True,
        "follow_internal_links": True,
        "follow_external_links": False,
        "extract_full_html": False,
        "include_images": False,
        "save_to_database": False
    }
    
    print(f"🔍 Testing domain crawl for: {url}")
    print(f"📋 Config: {json.dumps(config, indent=2)}")
    
    try:
        result = await engine.intelligent_crawl(url, "basic", config)
        
        print(f"\n✅ Crawl completed!")
        print(f"📊 Pages processed: {result['summary']['pages_processed']}")
        print(f"🔗 URLs discovered: {result['summary']['urls_discovered']}")
        print(f"📋 URLs queued: {result['summary']['urls_queued']}")
        print(f"🌐 Domains crawled: {len(result['summary']['domains_crawled'])}")
        
        if result['summary']['urls_discovered'] > 0:
            print(f"\n🔗 First 5 discovered URLs:")
            for i, url in enumerate(result['discovered_urls'][:5]):
                print(f"  {i+1}. {url}")
        else:
            print("\n❌ No URLs discovered!")
            
        if result['crawled_data']:
            print(f"\n📄 First page data keys: {list(result['crawled_data'][0].keys())}")
            if 'links' in result['crawled_data'][0]:
                links = result['crawled_data'][0]['links']
                print(f"📎 Links found on first page: {len(links)}")
                for i, link in enumerate(links[:3]):
                    print(f"  {i+1}. {link}")
            else:
                print("❌ No 'links' key in page data!")
        
        return result
        
    except Exception as e:
        print(f"❌ Error during crawl: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    asyncio.run(test_domain_crawl())
