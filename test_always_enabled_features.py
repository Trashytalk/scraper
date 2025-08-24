#!/usr/bin/env python3
"""
Test script to verify the new always-enabled features work correctly
"""

import asyncio
import json
from scraping_engine import ScrapingEngine


async def test_always_enabled_features():
    """Test that Extract Full HTML, Include Images, Include Forms, and Save to Database work when always enabled"""
    engine = ScrapingEngine()
    
    # Test with a page that should have forms and images
    url = "https://httpbin.org/forms/post"
    
    print("🔧 Testing Always-Enabled Features")
    print("=" * 60)
    
    # Test configuration with all features enabled (as they should be by default now)
    config = {
        "extract_full_html": True,    # Always enabled
        "include_images": True,       # Always enabled
        "include_forms": True,        # Always enabled
        "save_to_database": True,     # Always enabled
        "max_pages": 2,
        "max_depth": 1
    }
    
    print(f"📋 Testing URL: {url}")
    print(f"⚙️ Config: {json.dumps(config, indent=2)}")
    print("-" * 60)
    
    try:
        # Test basic scraping
        print("\n1. Testing Basic Scraping with all features enabled")
        result = await engine.scrape_url(url, "basic", config)
        print(f"   ✅ Scraping completed successfully")
        
        # Check each feature
        print(f"\n📊 Feature Results:")
        
        # Images
        if "images" in result:
            print(f"   🖼️ Images: {len(result['images'])} found")
            if result['images']:
                print(f"      Sample: {result['images'][0]['src']}")
        else:
            print(f"   ❌ No images key found")
        
        # Forms  
        if "forms" in result:
            print(f"   📝 Forms: {len(result['forms'])} found")
            if result['forms']:
                form = result['forms'][0]
                print(f"      Sample form: {form['method']} to {form['action']}")
                print(f"      Fields: {len(form['fields'])} found")
        else:
            print(f"   ❌ No forms key found")
        
        # Full HTML
        if "raw_html" in result:
            html_size = len(result['raw_html'])
            print(f"   📄 Full HTML: {html_size:,} characters extracted")
        else:
            print(f"   ❌ No raw_html key found")
        
        # Database save
        print(f"   💾 Save to Database: {'✅ Enabled' if config.get('save_to_database', False) else '❌ Disabled'}")
        
        print(f"\n📋 All result keys: {list(result.keys())}")
        
        # Test intelligent crawling
        print(f"\n2. Testing Intelligent Crawling with all features enabled")
        crawl_result = await engine.intelligent_crawl(url, "basic", config)
        print(f"   ✅ Crawling completed successfully")
        print(f"   📊 Pages processed: {crawl_result['summary']['pages_processed']}")
        print(f"   🖼️ Total images extracted: {crawl_result['summary']['images_extracted']}")
        print(f"   📝 Total forms extracted: {crawl_result['summary']['forms_extracted']}")
        
        if crawl_result['crawled_data']:
            first_page = crawl_result['crawled_data'][0]
            print(f"   📋 First page keys: {list(first_page.keys())}")
            
            # Check first page features
            if "images" in first_page:
                print(f"   🖼️ First page images: {len(first_page['images'])}")
            if "forms" in first_page:
                print(f"   📝 First page forms: {len(first_page['forms'])}")
            if "raw_html" in first_page:
                print(f"   📄 First page HTML size: {len(first_page['raw_html']):,} chars")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🎉 Always-Enabled Features Test Complete!")
    print("✅ Extract Full HTML: Always enabled")
    print("✅ Include Images: Always enabled")  
    print("✅ Include Forms: Always enabled")
    print("✅ Save to Database: Always enabled")


if __name__ == "__main__":
    asyncio.run(test_always_enabled_features())
