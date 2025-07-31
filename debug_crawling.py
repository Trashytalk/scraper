#!/usr/bin/env python3
"""
Debug Crawling Test Script
Tests the intelligent crawling functionality to identify issues
"""

import asyncio
import json
from scraping_engine import ScrapingEngine

async def test_crawling():
    print("🔍 Testing Intelligent Crawling Functionality")
    print("=" * 50)
    
    engine = ScrapingEngine()
    
    # Test 1: Basic scraping to ensure URL fetching works
    print("\n1. Testing basic scraping (httpbin.org)...")
    basic_result = await engine.scrape_url("https://httpbin.org/html", "basic")
    print(f"   Basic scraping status: {basic_result.get('status')}")
    print(f"   Links found: {len(basic_result.get('links', []))}")
    
    if basic_result.get('links'):
        print("   Sample links:")
        for i, link in enumerate(basic_result['links'][:3]):
            print(f"     {i+1}. {link}")
    
    # Test 2: Intelligent crawling with small limits
    print("\n2. Testing intelligent crawling (example.com)...")
    crawl_config = {
        "max_pages": 3,
        "max_depth": 2,
        "follow_internal_links": True,
        "follow_external_links": False,
        "rate_limit": {"requests_per_second": 2.0}
    }
    
    crawl_result = await engine.intelligent_crawl(
        "https://example.com", 
        "basic", 
        crawl_config
    )
    
    print(f"   Crawling status: {crawl_result.get('status')}")
    print(f"   Job type: {crawl_result.get('job_type')}")
    print("\n   Summary:")
    summary = crawl_result.get('summary', {})
    for key, value in summary.items():
        print(f"     {key}: {value}")
    
    print(f"\n   Pages crawled: {len(crawl_result.get('crawled_data', []))}")
    print(f"   URLs discovered: {len(crawl_result.get('discovered_urls', []))}")
    print(f"   Errors: {len(crawl_result.get('errors', []))}")
    
    if crawl_result.get('discovered_urls'):
        print("\n   Discovered URLs:")
        for i, url in enumerate(crawl_result['discovered_urls'][:5]):
            print(f"     {i+1}. {url}")
    
    if crawl_result.get('errors'):
        print("\n   Errors encountered:")
        for error in crawl_result['errors']:
            print(f"     - {error['url']}: {error['error']}")
    
    # Test 3: Test with a site that has more links
    print("\n3. Testing with a site that has more links (httpbin.org)...")
    crawl_config_httpbin = {
        "max_pages": 5,
        "max_depth": 2,
        "follow_internal_links": True,
        "follow_external_links": True,  # Allow external to see more links
        "rate_limit": {"requests_per_second": 1.0}
    }
    
    httpbin_result = await engine.intelligent_crawl(
        "https://httpbin.org", 
        "basic", 
        crawl_config_httpbin
    )
    
    print(f"   HTTPBin crawling status: {httpbin_result.get('status')}")
    print("\n   HTTPBin Summary:")
    summary = httpbin_result.get('summary', {})
    for key, value in summary.items():
        print(f"     {key}: {value}")
    
    print(f"\n   HTTPBin URLs discovered: {len(httpbin_result.get('discovered_urls', []))}")
    if httpbin_result.get('discovered_urls'):
        print("   Sample discovered URLs:")
        for i, url in enumerate(httpbin_result['discovered_urls'][:3]):
            print(f"     {i+1}. {url}")

if __name__ == "__main__":
    asyncio.run(test_crawling())
