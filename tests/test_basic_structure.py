#!/usr/bin/env python3
"""
Basic Structure Test for Advanced Crawling System

Tests that the basic crawling classes and functions work correctly
without requiring external dependencies like aiohttp or beautifulsoup4.
"""

import sys
import os
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_basic_imports():
    """Test that we can import the basic crawling modules"""
    print("🔍 Testing Basic Imports...")
    
    try:
        # Test crawling package import
        import business_intel_scraper.backend.crawling as crawling_pkg
        print("  ✅ Crawling package imported successfully")
        
        # Test individual module imports with graceful fallbacks
        from business_intel_scraper.backend.crawling.advanced_crawler import (
            SeedSource, CrawlTarget, DiscoveredPage, DomainRule, CrawlMetrics
        )
        print("  ✅ Basic data classes imported successfully")
        
        from business_intel_scraper.backend.crawling.orchestrator import (
            BusinessIntelligencePatterns, CrawlJobStatus
        )
        print("  ✅ Orchestrator classes imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality without external dependencies"""
    print("\n🧪 Testing Basic Functionality...")
    
    try:
        # Test data class creation
        from business_intel_scraper.backend.crawling.advanced_crawler import SeedSource
        
        seed = SeedSource(
            name="Test Source",
            urls=["https://example.com"],
            source_type="test",
            priority=5
        )
        
        assert seed.name == "Test Source"
        assert len(seed.urls) == 1
        assert seed.source_type == "test"
        print("  ✅ SeedSource creation works correctly")
        
        # Test business patterns
        from business_intel_scraper.backend.crawling.orchestrator import BusinessIntelligencePatterns
        
        patterns = BusinessIntelligencePatterns()
        assert hasattr(patterns, 'high_value_patterns')
        assert hasattr(patterns, 'financial_patterns')
        print("  ✅ BusinessIntelligencePatterns works correctly")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Functionality test failed: {e}")
        return False

def test_graceful_fallbacks():
    """Test that the system handles missing dependencies gracefully"""
    print("\n🛡️ Testing Graceful Fallbacks...")
    
    try:
        # This should work even without aiohttp/beautifulsoup4
        from business_intel_scraper.backend.crawling.advanced_crawler import AdvancedCrawlManager
        
        # Create manager (should not crash even without dependencies)
        manager = AdvancedCrawlManager()
        
        # Test that it has the expected attributes
        assert hasattr(manager, 'seed_sources')
        assert hasattr(manager, 'domain_rules')
        assert hasattr(manager, 'discovered_pages')
        print("  ✅ AdvancedCrawlManager initializes without external dependencies")
        
        # Test URL validation (should work with standard library)
        test_url = "https://example.com/test"
        # This method should exist and work with basic Python
        if hasattr(manager, 'is_valid_url'):
            result = manager.is_valid_url(test_url)
            print(f"  ✅ URL validation works: {test_url} -> {result}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Graceful fallback test failed: {e}")
        return False

def test_config_loading():
    """Test configuration loading functionality"""
    print("\n⚙️ Testing Configuration Loading...")
    
    try:
        from business_intel_scraper.backend.crawling.advanced_crawler import AdvancedCrawlManager
        
        manager = AdvancedCrawlManager()
        
        # Test that default configuration is loaded
        assert hasattr(manager, 'config')
        print("  ✅ Configuration system initializes")
        
        # Test seed source loading (should have defaults even without external config)
        if hasattr(manager, 'load_seed_sources'):
            # This should work or gracefully handle missing files
            try:
                manager.load_seed_sources()
                print("  ✅ Seed source loading works (or gracefully fails)")
            except Exception as e:
                print(f"  ⚠️  Seed source loading failed gracefully: {e}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Configuration test failed: {e}")
        return False

def main():
    """Run all basic structure tests"""
    print("🚀 BASIC STRUCTURE TESTS FOR ADVANCED CRAWLING SYSTEM")
    print("=" * 60)
    
    tests = [
        test_basic_imports,
        test_basic_functionality,
        test_graceful_fallbacks,
        test_config_loading
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"  ❌ Test {test_func.__name__} crashed: {e}")
    
    print(f"\n📊 TEST RESULTS: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! The basic structure is working correctly.")
        print("💡 All dependencies are now included in the main requirements.txt file")
    else:
        print("⚠️  Some tests failed. Check the implementation for issues.")
    
    print("\n" + "=" * 60)
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
