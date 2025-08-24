#!/usr/bin/env python3
"""
Test script focused on image extraction with always-enabled features
"""

import asyncio
import json
from scraping_engine import ScrapingEngine


async def test_image_extraction():
    """Test that image extraction works correctly when always enabled"""
    engine = ScrapingEngine()
    
    # Test with Wikipedia page which should have images
    url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
    
    print("🖼️ Testing Image Extraction (Always Enabled)")
    print("=" * 60)
    
    config = {
        "extract_full_html": True,    # Always enabled
        "include_images": True,       # Always enabled
        "include_forms": True,        # Always enabled
        "save_to_database": True,     # Always enabled
        "max_pages": 1,
        "max_depth": 1
    }
    
    print(f"📋 Testing URL: {url}")
    print("-" * 60)
    
    try:
        # Test basic scraping
        result = await engine.scrape_url(url, "basic", config)
        print(f"✅ Scraping completed successfully")
        
        # Check images specifically
        if "images" in result:
            images = result['images']
            print(f"🖼️ Images found: {len(images)}")
            
            if images:
                print(f"\n📸 Sample images:")
                for i, img in enumerate(images[:3]):  # Show first 3
                    print(f"   {i+1}. {img['src']}")
                    if 'alt' in img and img['alt']:
                        print(f"      Alt: {img['alt']}")
        else:
            print(f"❌ No images key found in result")
        
        # Check forms
        if "forms" in result:
            forms = result['forms']
            print(f"📝 Forms found: {len(forms)}")
            
            if forms:
                print(f"\n📋 Sample forms:")
                for i, form in enumerate(forms[:2]):  # Show first 2
                    print(f"   {i+1}. {form['method']} to {form['action']}")
                    print(f"      Fields: {len(form['fields'])}")
        
        # Check HTML
        if "raw_html" in result:
            html_size = len(result['raw_html'])
            print(f"📄 Full HTML: {html_size:,} characters extracted")
        
        print(f"\n📊 Total result keys: {len(result.keys())}")
        print(f"📋 Keys: {', '.join(sorted(result.keys()))}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🎉 Image Extraction Test Complete!")


if __name__ == "__main__":
    asyncio.run(test_image_extraction())
