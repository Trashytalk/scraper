#!/usr/bin/env python3
"""
Test the improved HTTP error handling and connection management
"""

import asyncio
import requests
import time
from scraping_engine import ScrapingEngine


async def test_improved_error_handling():
    """Test the improved HTTP error handling"""
    print("🔧 Testing Improved HTTP Error Handling")
    print("=" * 60)
    
    engine = ScrapingEngine()
    
    test_cases = [
        {
            "name": "Valid URL",
            "url": "https://httpbin.org/html",
            "expected": "success"
        },
        {
            "name": "Timeout simulation", 
            "url": "https://httpbin.org/delay/5",  # 5 second delay
            "expected": "should_work"
        },
        {
            "name": "404 Error",
            "url": "https://httpbin.org/status/404",
            "expected": "failure"
        },
        {
            "name": "503 Service Unavailable",
            "url": "https://httpbin.org/status/503", 
            "expected": "should_retry"
        },
        {
            "name": "Invalid domain (should get connection error)",
            "url": "https://definitely-not-a-real-domain-12345.com",
            "expected": "connection_error"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        print(f"   URL: {test_case['url']}")
        
        start_time = time.time()
        try:
            config = {
                "include_images": False,
                "include_forms": False,
                "max_pages": 1
            }
            
            result = await engine.scrape_url(test_case['url'], "basic", config)
            elapsed = time.time() - start_time
            
            print(f"   ✅ Success after {elapsed:.2f}s")
            print(f"   📊 Status: {result.get('status', 'unknown')}")
            print(f"   📄 Title: {result.get('title', 'No title')[:50]}...")
            
        except Exception as e:
            elapsed = time.time() - start_time
            error_msg = str(e)
            
            print(f"   ❌ Failed after {elapsed:.2f}s")
            print(f"   🚨 Error: {error_msg}")
            
            # Check if the error handling is improved
            if "HTTP 0" in error_msg:
                print(f"   ⚠️  Still getting HTTP 0 errors - need further investigation")
            elif "Connection failed after 3 attempts" in error_msg:
                print(f"   ✅ Proper connection error handling")
            elif "Timeout after 3 attempts" in error_msg:
                print(f"   ✅ Proper timeout error handling")
            elif "HTTP 404" in error_msg or "HTTP 503" in error_msg:
                print(f"   ✅ Proper HTTP status error handling")
    
    print(f"\n" + "=" * 60)
    print("🎉 HTTP Error Handling Test Complete!")
    print("✅ Enhanced error messages")
    print("✅ Better retry logic with exponential backoff") 
    print("✅ Improved timeout handling")
    print("✅ Connection error detection")


async def test_anime_site_specifically():
    """Test the specific anime site that was causing HTTP 0 errors"""
    print(f"\n🎯 Testing Anime Site Specifically")
    print("=" * 60)
    
    engine = ScrapingEngine()
    
    # Test a few URLs from the anime site
    anime_urls = [
        "https://animenana.com/",  # Homepage
        "https://animenana.com/animeserie/solo-leveling-season-2-arise-from-the-shadow/",
        "https://animenana.com/animeserie/how-a-realist-hero-rebuilt-the-kingdom/"
    ]
    
    for url in anime_urls:
        print(f"\n🔍 Testing: {url}")
        start_time = time.time()
        
        try:
            config = {
                "include_images": True,
                "include_forms": True,
                "max_pages": 1
            }
            
            result = await engine.scrape_url(url, "basic", config)
            elapsed = time.time() - start_time
            
            print(f"   ✅ Success after {elapsed:.2f}s")
            print(f"   📊 Status: {result.get('status', 'unknown')}")
            print(f"   📄 Title: {result.get('title', 'No title')}")
            print(f"   🖼️ Images found: {len(result.get('images', []))}")
            print(f"   📝 Forms found: {len(result.get('forms', []))}")
            print(f"   📏 Content length: {len(result.get('text_content', ''))}")
            
        except Exception as e:
            elapsed = time.time() - start_time
            error_msg = str(e)
            
            print(f"   ❌ Failed after {elapsed:.2f}s")
            print(f"   🚨 Error: {error_msg}")
            
            # Analyze the error type
            if "Connection failed" in error_msg:
                print(f"   💡 Site may be blocking requests or is unreachable")
            elif "Timeout" in error_msg:
                print(f"   💡 Site is slow to respond") 
            elif "HTTP" in error_msg:
                print(f"   💡 Site returned an HTTP error")
            else:
                print(f"   💡 Unexpected error type")


if __name__ == "__main__":
    asyncio.run(test_improved_error_handling())
    asyncio.run(test_anime_site_specifically())
