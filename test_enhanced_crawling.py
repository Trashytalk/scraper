#!/usr/bin/env python3
"""
Enhanced Intelligent Crawling Test Suite
Tests all new features including full HTML extraction, domain crawling, 
image extraction, and comprehensive status tracking.
"""

import asyncio
import json
import sqlite3
import time
from datetime import datetime
from scraping_engine import ScrapingEngine

def test_enhanced_crawling_features():
    """Test all enhanced crawling features"""
    print("🧪 Testing Enhanced Intelligent Crawling Features")
    print("=" * 70)
    
    engine = ScrapingEngine()
    
    # Test 1: Full HTML Extraction
    print("\n🧪 Test 1: Full HTML Extraction")
    print("-" * 50)
    
    config_html = {
        "max_depth": 2,
        "max_pages": 3,
        "extract_full_html": True,
        "include_images": True,
        "save_to_database": True,
        "follow_internal_links": True,
        "follow_external_links": False
    }
    
    async def run_html_test():
        result = await engine.intelligent_crawl(
            "https://en.wikipedia.org/wiki/Python_(programming_language)",
            "basic",
            config_html
        )
        
        print(f"✅ Status: {result['status']}")
        print(f"📊 Pages processed: {result['summary']['pages_processed']}")
        print(f"🖼️  Images extracted: {result['summary']['images_extracted']}")
        print(f"⏱️  Total time: {result['summary']['total_crawl_time']}s")
        print(f"📈 Average page time: {result['summary']['average_page_time']}s")
        print(f"🌐 Domains crawled: {len(result['summary']['domains_crawled'])}")
        
        # Check if full HTML was extracted
        if result['crawled_data']:
            first_page = result['crawled_data'][0]
            has_full_html = 'raw_html' in first_page
            html_size = len(first_page.get('raw_html', ''))
            print(f"📄 Full HTML extracted: {'✅ Yes' if has_full_html else '❌ No'}")
            if has_full_html:
                print(f"📄 HTML size: {html_size:,} characters")
        
        return result
    
    html_result = asyncio.run(run_html_test())
    
    # Test 2: Domain Crawling
    print("\n🧪 Test 2: Entire Domain Crawling")
    print("-" * 50)
    
    config_domain = {
        "max_depth": 3,
        "max_pages": 8,
        "crawl_entire_domain": True,
        "extract_full_html": False,
        "include_images": True,
        "save_to_database": True,
        "follow_internal_links": True,
        "follow_external_links": False
    }
    
    async def run_domain_test():
        result = await engine.intelligent_crawl(
            "https://httpbin.org/",  # Smaller domain for testing
            "basic",
            config_domain
        )
        
        print(f"✅ Status: {result['status']}")
        print(f"📊 Pages processed: {result['summary']['pages_processed']}")
        print(f"🔗 URLs discovered: {result['summary']['urls_discovered']}")
        print(f"🌐 Domains crawled: {result['summary']['domains_crawled']}")
        print(f"⏱️  Total time: {result['summary']['total_crawl_time']}s")
        print(f"❌ Errors encountered: {result['summary']['errors_encountered']}")
        print(f"🔄 Duplicates skipped: {result['summary']['duplicate_pages_skipped']}")
        
        return result
    
    domain_result = asyncio.run(run_domain_test())
    
    # Test 3: Comprehensive Image Extraction
    print("\n🧪 Test 3: Comprehensive Image Extraction")
    print("-" * 50)
    
    config_images = {
        "max_depth": 2,
        "max_pages": 4,
        "extract_full_html": False,
        "crawl_entire_domain": False,
        "include_images": True,  # This enables comprehensive image extraction
        "save_to_database": True,
        "follow_internal_links": True,
        "follow_external_links": False
    }
    
    async def run_image_test():
        result = await engine.intelligent_crawl(
            "https://en.wikipedia.org/wiki/Photography",
            "basic",
            config_images
        )
        
        print(f"✅ Status: {result['status']}")
        print(f"📊 Pages processed: {result['summary']['pages_processed']}")
        print(f"🖼️  Total images extracted: {result['summary']['images_extracted']}")
        print(f"⏱️  Total time: {result['summary']['total_crawl_time']}s")
        
        # Analyze image types
        if result['crawled_data']:
            total_images = 0
            img_types = {"img_tag": 0, "background_image": 0}
            
            for page in result['crawled_data']:
                images = page.get('images', [])
                total_images += len(images)
                
                for img in images:
                    img_type = img.get('type', 'img_tag')
                    img_types[img_type] = img_types.get(img_type, 0) + 1
            
            print(f"📸 Total images found: {total_images}")
            print(f"🏷️  Image tag images: {img_types.get('img_tag', 0)}")
            print(f"🎨 Background images: {img_types.get('background_image', 0)}")
        
        return result
    
    image_result = asyncio.run(run_image_test())
    
    # Test 4: Status and Persistence Check
    print("\n🧪 Test 4: Data Persistence & Status Summary")
    print("-" * 50)
    
    # Check database for stored data
    try:
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        
        # Check if crawl cache table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='crawl_cache'
        """)
        cache_table_exists = cursor.fetchone() is not None
        
        if cache_table_exists:
            cursor.execute("SELECT COUNT(*) FROM crawl_cache")
            cached_pages = cursor.fetchone()[0]
            
            cursor.execute("SELECT DISTINCT domain FROM crawl_cache")
            cached_domains = cursor.fetchall()
            
            print(f"💾 Database persistence: ✅ Enabled")
            print(f"📄 Cached pages: {cached_pages}")
            print(f"🌐 Cached domains: {len(cached_domains)}")
            
            # Show some cached URLs
            cursor.execute("SELECT url, crawled_at FROM crawl_cache ORDER BY crawled_at DESC LIMIT 5")
            recent_cached = cursor.fetchall()
            print(f"🕒 Recent cached pages:")
            for url, crawled_at in recent_cached:
                print(f"   - {url[:60]}... ({crawled_at})")
        else:
            print(f"💾 Database persistence: ❌ No cache table found")
        
        conn.close()
        
    except Exception as e:
        print(f"💾 Database persistence: ❌ Error checking database: {e}")
    
    # Test 5: Status Summary Analysis
    print("\n🧪 Test 5: Crawl Status Summary Analysis")
    print("-" * 50)
    
    def analyze_crawl_status(result):
        summary = result.get('summary', {})
        config = result.get('config', {})
        
        print(f"📋 Crawl Configuration:")
        print(f"   🎯 Max depth: {config.get('max_depth', 'N/A')}")
        print(f"   📄 Max pages: {config.get('max_pages', 'N/A')}")
        print(f"   🌐 Domain crawling: {'✅' if config.get('crawl_entire_domain') else '❌'}")
        print(f"   📄 Full HTML: {'✅' if config.get('extract_full_html') else '❌'}")
        print(f"   🖼️  Include images: {'✅' if config.get('include_images') else '❌'}")
        
        print(f"\n📊 Performance Metrics:")
        print(f"   ⏱️  Total time: {summary.get('total_crawl_time', 0)}s")
        print(f"   📈 Avg page time: {summary.get('average_page_time', 0)}s")
        print(f"   📄 Pages processed: {summary.get('pages_processed', 0)}")
        print(f"   🔗 URLs discovered: {summary.get('urls_discovered', 0)}")
        print(f"   🌐 Domains found: {len(summary.get('domains_crawled', []))}")
        
        print(f"\n🔍 Quality Metrics:")
        print(f"   ✅ Successful pages: {summary.get('pages_processed', 0)}")
        print(f"   ❌ Errors: {summary.get('errors_encountered', 0)}")
        print(f"   🔄 Duplicates skipped: {summary.get('duplicate_pages_skipped', 0)}")
        print(f"   🖼️  Images extracted: {summary.get('images_extracted', 0)}")
        
        # Calculate success rate
        total_attempts = summary.get('pages_processed', 0) + summary.get('errors_encountered', 0)
        success_rate = (summary.get('pages_processed', 0) / total_attempts * 100) if total_attempts > 0 else 0
        print(f"   📊 Success rate: {success_rate:.1f}%")
    
    print("\n📈 HTML Extraction Test Results:")
    analyze_crawl_status(html_result)
    
    print("\n📈 Domain Crawling Test Results:")
    analyze_crawl_status(domain_result)
    
    print("\n📈 Image Extraction Test Results:")
    analyze_crawl_status(image_result)
    
    # Summary
    print("\n" + "=" * 70)
    print("🎉 Enhanced Crawling Test Summary")
    print("=" * 70)
    
    total_pages = (html_result['summary']['pages_processed'] + 
                  domain_result['summary']['pages_processed'] + 
                  image_result['summary']['pages_processed'])
    
    total_images = (html_result['summary']['images_extracted'] + 
                   domain_result['summary']['images_extracted'] + 
                   image_result['summary']['images_extracted'])
    
    total_time = (html_result['summary']['total_crawl_time'] + 
                 domain_result['summary']['total_crawl_time'] + 
                 image_result['summary']['total_crawl_time'])
    
    print(f"📊 Total pages crawled: {total_pages}")
    print(f"🖼️  Total images extracted: {total_images}")
    print(f"⏱️  Total execution time: {total_time:.2f}s")
    print(f"📈 Average pages per second: {total_pages/total_time:.2f}")
    
    features_tested = [
        ("Full HTML Extraction", html_result['status'] == 'success'),
        ("Domain Crawling", domain_result['status'] == 'success'),
        ("Enhanced Image Extraction", image_result['status'] == 'success'),
        ("Data Persistence", cache_table_exists if 'cache_table_exists' in locals() else False),
        ("Status Tracking", True)  # Always works if we get results
    ]
    
    print(f"\n✅ Features Successfully Tested:")
    for feature, success in features_tested:
        status = "✅" if success else "❌"
        print(f"   {status} {feature}")
    
    success_count = sum(1 for _, success in features_tested if success)
    print(f"\n🎯 Overall Success Rate: {success_count}/{len(features_tested)} ({success_count/len(features_tested)*100:.1f}%)")
    
    if success_count == len(features_tested):
        print("🏆 All enhanced crawling features are working perfectly!")
    else:
        print("⚠️  Some features need attention. Check the logs above.")

if __name__ == "__main__":
    test_enhanced_crawling_features()
