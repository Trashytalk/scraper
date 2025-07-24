#!/usr/bin/env python3
"""
Test script to verify URL extraction functionality
"""

import json

def extract_urls_from_crawler(job_data):
    """
    Test version of the URL extraction function from the frontend
    """
    urls = []
    
    # Define possible URL field names
    possible_url_fields = [
        'url', 'link', 'href', 'page_url', 'discovered_url', 'target_url',
        'source_url', 'canonical_url', 'original_url', 'crawled_url',
        'found_url', 'extracted_url', 'site_url', 'web_url', 'full_url',
        'absolute_url', 'final_url', 'redirect_url', 'destination_url'
    ]
    
    print(f"🔍 Analyzing job: {job_data.get('name', 'Unknown')}")
    print(f"📊 Job status: {job_data.get('status', 'Unknown')}")
    print(f"📈 Items collected: {job_data.get('items_collected', 0)}")
    
    # Check if job has results
    if 'results' not in job_data or not job_data['results']:
        print("❌ No results found in job data")
        return urls
    
    results = job_data['results']
    print(f"📋 Found {len(results)} result items")
    
    for i, item in enumerate(results):
        print(f"\n--- Processing item {i+1} ---")
        print(f"Item type: {type(item)}")
        
        if isinstance(item, dict):
            print(f"Item keys: {list(item.keys())}")
            
            # Check each possible URL field
            for field in possible_url_fields:
                if field in item:
                    value = item[field]
                    print(f"Found field '{field}': {value} (type: {type(value)})")
                    
                    if isinstance(value, str) and (value.startswith('http://') or value.startswith('https://')):
                        urls.append(value)
                        print(f"✅ Added URL from field '{field}': {value}")
                        break
                    elif isinstance(value, list):
                        print(f"Field '{field}' is a list with {len(value)} items")
                        for url_item in value:
                            if isinstance(url_item, str) and (url_item.startswith('http://') or url_item.startswith('https://')):
                                urls.append(url_item)
                                print(f"✅ Added URL from list field '{field}': {url_item}")
            
            # Check for links array
            if 'links' in item and isinstance(item['links'], list):
                print(f"Found 'links' array with {len(item['links'])} items")
                for link_item in item['links']:
                    if isinstance(link_item, str) and (link_item.startswith('http://') or link_item.startswith('https://')):
                        urls.append(link_item)
                        print(f"✅ Added URL from links array: {link_item}")
                    elif isinstance(link_item, dict):
                        for field in possible_url_fields:
                            if field in link_item and isinstance(link_item[field], str):
                                if link_item[field].startswith('http://') or link_item[field].startswith('https://'):
                                    urls.append(link_item[field])
                                    print(f"✅ Added URL from link object field '{field}': {link_item[field]}")
                                    break
        else:
            print(f"Item is not a dictionary: {item}")
    
    # Remove duplicates
    unique_urls = list(set(urls))
    print(f"\n🎯 Total URLs found: {len(urls)}")
    print(f"🎯 Unique URLs: {len(unique_urls)}")
    
    return unique_urls

def test_url_extraction():
    """Test the URL extraction with sample data"""
    
    # Test case 1: Simple URL field
    test_data_1 = {
        "name": "Test Job 1",
        "status": "completed",
        "items_collected": 3,
        "results": [
            {"url": "https://example.com/page1", "title": "Page 1"},
            {"url": "https://example.com/page2", "title": "Page 2"},
            {"link": "https://example.com/page3", "title": "Page 3"}
        ]
    }
    
    print("=" * 60)
    print("TEST CASE 1: Simple URL fields")
    print("=" * 60)
    urls_1 = extract_urls_from_crawler(test_data_1)
    print(f"Result: {urls_1}")
    
    # Test case 2: Nested links
    test_data_2 = {
        "name": "Test Job 2", 
        "status": "completed",
        "items_collected": 2,
        "results": [
            {
                "page_info": {"canonical_url": "https://site.com/article1"},
                "links": [
                    "https://site.com/related1",
                    {"href": "https://site.com/related2", "text": "Link 2"}
                ]
            },
            {
                "discovered_url": "https://site.com/article2",
                "metadata": {"source_url": "https://site.com/source"}
            }
        ]
    }
    
    print("\n" + "=" * 60)
    print("TEST CASE 2: Nested and complex structures")
    print("=" * 60)
    urls_2 = extract_urls_from_crawler(test_data_2)
    print(f"Result: {urls_2}")
    
    # Test case 3: User's actual data structure
    test_data_3 = {
        "name": "User's Crawler Job",
        "status": "completed", 
        "items_collected": 50,
        "results": [
            {"crawled_url": "https://target-site.com/page1", "content": "Sample content"},
            {"page_url": "https://target-site.com/page2", "links_found": ["https://target-site.com/sub1"]},
            {"url": "https://target-site.com/page3", "timestamp": "2024-01-01"}
        ]
    }
    
    print("\n" + "=" * 60)
    print("TEST CASE 3: User's actual data structure simulation")
    print("=" * 60)
    urls_3 = extract_urls_from_crawler(test_data_3)
    print(f"Result: {urls_3}")

if __name__ == "__main__":
    test_url_extraction()
