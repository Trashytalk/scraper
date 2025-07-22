#!/usr/bin/env python3
"""
Spider Marketplace Demo Script
Demonstrates the marketplace functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from business_intel_scraper.backend.marketplace import SpiderMarketplace

def main():
    print("🕷️  Spider Marketplace Demo")
    print("=" * 40)
    
    try:
        # Initialize marketplace
        print("🔧 Initializing marketplace...")
        mp = SpiderMarketplace()
        print("✅ Marketplace initialized successfully!")
        
        # Show stats
        print("\n📊 Marketplace Statistics:")
        stats = mp.get_marketplace_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Show categories
        print("\n🏷️  Available Categories:")
        categories = mp.get_categories()
        for i, cat in enumerate(categories[:8], 1):
            print(f"  {i}. {cat}")
        if len(categories) > 8:
            print(f"  ... and {len(categories) - 8} more")
        
        # Search spiders
        print("\n🔍 Featured Spiders:")
        spiders = mp.search_spiders(limit=5)
        for spider in spiders:
            verified = "✅" if spider.get('verified') else "⚠️"
            installed = "💾" if spider.get('installed') else "📦"
            rating = f"⭐{spider.get('rating', 0):.1f}" if spider.get('rating') else "⭐N/A"
            downloads = f"📥{spider.get('downloads', 0):,}" if spider.get('downloads') else "📥0"
            
            print(f"  {verified} {installed} {spider['name']} v{spider['version']}")
            print(f"      by {spider['author']} | {rating} | {downloads}")
            print(f"      {spider['description'][:60]}...")
            print()
        
        # Demo installation
        print("🚀 Demo Installation:")
        test_spider = spiders[0] if spiders else None
        if test_spider and not test_spider.get('installed'):
            print(f"Installing {test_spider['name']}...")
            result = mp.install_spider(test_spider['name'], test_spider['version'])
            if result['success']:
                print(f"✅ {result['message']}")
            else:
                print(f"❌ {result['error']}")
        else:
            print("📋 No spiders available for demo installation")
        
        # Show installed spiders
        print("\n💾 Installed Spiders:")
        installed = mp.list_installed_spiders()
        if installed:
            for spider in installed:
                print(f"  ✅ {spider['name']} v{spider['version']} ({spider['category']})")
        else:
            print("  No spiders currently installed")
        
        print("\n🎉 Marketplace demo completed successfully!")
        print("💡 Try the web interface at http://localhost:3000/marketplace")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
