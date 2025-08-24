#!/usr/bin/env python3
"""
Debug script to test image extraction functionality
"""

import asyncio
import json
from scraping_engine import ScrapingEngine


async def test_image_extraction():
    """Test image extraction with different configurations"""
    engine = ScrapingEngine()
    
    # Test with a page that should have images
    url = "https://en.wikipedia.org/wiki/Web_scraping"
    
    print("🖼️ Testing Image Extraction")
    print("=" * 50)
    
    # Test 1: Without image extraction
    print("\n1. Testing WITHOUT image extraction")
    config1 = {
        "include_images": False,
        "include_all_images": False,
        "save_to_database": False
    }
    
    try:
        result1 = await engine.scrape_url(url, "basic", config1)
        print(f"   ✅ Scraping completed")
        
        if "images" in result1:
            print(f"   📊 Images found: {len(result1['images'])}")
            if result1['images']:
                print(f"   🖼️ First image: {result1['images'][0]}")
            else:
                print("   ❌ No images extracted")
        else:
            print("   ❌ No 'images' key in result")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: With basic image extraction
    print("\n2. Testing WITH basic image extraction")
    config2 = {
        "include_images": True,
        "include_all_images": False,
        "save_to_database": False
    }
    
    try:
        result2 = await engine.scrape_url(url, "basic", config2)
        print(f"   ✅ Scraping completed")
        
        if "images" in result2:
            print(f"   📊 Images found: {len(result2['images'])}")
            if result2['images']:
                print(f"   🖼️ First image: {result2['images'][0]}")
                print(f"   🖼️ Sample images:")
                for i, img in enumerate(result2['images'][:3]):
                    print(f"      {i+1}. {img.get('src', 'No src')} (alt: {img.get('alt', 'No alt')})")
            else:
                print("   ❌ No images extracted")
        else:
            print("   ❌ No 'images' key in result")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: With comprehensive image extraction
    print("\n3. Testing WITH comprehensive image extraction")
    config3 = {
        "include_images": True,
        "include_all_images": True,
        "save_to_database": False
    }
    
    try:
        result3 = await engine.scrape_url(url, "basic", config3)
        print(f"   ✅ Scraping completed")
        
        if "images" in result3:
            print(f"   📊 Images found: {len(result3['images'])}")
            if result3['images']:
                print(f"   🖼️ First image: {result3['images'][0]}")
                print(f"   🖼️ Sample images:")
                for i, img in enumerate(result3['images'][:3]):
                    print(f"      {i+1}. {img.get('src', 'No src')} (alt: {img.get('alt', 'No alt')})")
            else:
                print("   ❌ No images extracted")
        else:
            print("   ❌ No 'images' key in result")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Test intelligent crawl with images
    print("\n4. Testing intelligent crawl WITH images")
    crawl_config = {
        "max_pages": 2,
        "max_depth": 1,
        "include_images": True,
        "save_to_database": False
    }
    
    try:
        result4 = await engine.intelligent_crawl(url, "basic", crawl_config)
        print(f"   ✅ Crawling completed")
        print(f"   📊 Pages processed: {result4['summary']['pages_processed']}")
        print(f"   📊 Images extracted: {result4['summary']['images_extracted']}")
        
        if result4['crawled_data']:
            first_page = result4['crawled_data'][0]
            if "images" in first_page:
                print(f"   🖼️ Images on first page: {len(first_page['images'])}")
                if first_page['images']:
                    print(f"   🖼️ Sample from first page:")
                    for i, img in enumerate(first_page['images'][:2]):
                        print(f"      {i+1}. {img.get('src', 'No src')}")
            else:
                print("   ❌ No 'images' key in first page data")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("📋 Image Extraction Test Complete")


if __name__ == "__main__":
    asyncio.run(test_image_extraction())
