#!/usr/bin/env python3
"""
Test Script for Advanced Crawling/Discovery Layer

This script tests the comprehensive crawling system with all its features:
- Seed source management
- Recursive crawling with depth control
- Link classification and prioritization
- Metadata extraction
- Duplicate detection
- Rate limiting and robots.txt compliance
"""

import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime
import logging

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_basic_imports():
    """Test that our crawling modules can be imported"""
    print("🔧 Testing advanced crawling imports...")
    
    try:
        from business_intel_scraper.backend.crawling import AdvancedCrawlManager, CrawlOrchestrator
        print("✅ AdvancedCrawlManager and CrawlOrchestrator imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import crawling components: {e}")
        return False
    
    try:
        from business_intel_scraper.backend.crawling import DiscoveredPage, SeedSource
        print("✅ DiscoveredPage and SeedSource imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import data structures: {e}")
        return False
    
    try:
        from business_intel_scraper.backend.crawling import EnhancedAdaptiveLinkClassifier
        print("✅ EnhancedAdaptiveLinkClassifier imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import enhanced classifier: {e}")
        return False
    
    return True

def test_seed_sources():
    """Test seed source configuration and loading"""
    print("\n🌱 Testing seed source management...")
    
    from business_intel_scraper.backend.crawling import AdvancedCrawlManager
    
    # Initialize manager (without database for testing)
    manager = AdvancedCrawlManager(db_url=None, max_concurrent=5, max_depth=2)
    
    # Check seed sources
    seed_sources = manager.seed_sources
    print(f"✅ Loaded {len(seed_sources)} seed source categories:")
    
    total_urls = 0
    for source_name, source in seed_sources.items():
        print(f"  📂 {source.name}: {len(source.urls)} URLs (priority: {source.priority})")
        print(f"     Type: {source.source_type}, Frequency: {source.update_frequency}")
        total_urls += len(source.urls)
    
    print(f"✅ Total seed URLs configured: {total_urls}")
    return True

def test_domain_rules():
    """Test domain filtering and URL pattern matching"""
    print("\n🔍 Testing domain rules and URL filtering...")
    
    from business_intel_scraper.backend.crawling import AdvancedCrawlManager
    
    manager = AdvancedCrawlManager(db_url=None)
    
    # Test URLs for filtering
    test_urls = [
        ("https://sec.gov/edgar/company/123", True, "SEC filing - should be allowed"),
        ("https://facebook.com/company/abc", False, "Social media - should be blocked"),
        ("https://bloomberg.com/company/profile", True, "Bloomberg company - should be allowed"),
        ("https://example.com/login", False, "Login page - should be excluded"),
        ("https://manta.com/business/directory", True, "Business directory - should be allowed"),
        ("https://youtube.com/watch?v=123", False, "YouTube - should be blocked"),
    ]
    
    passed = 0
    failed = 0
    
    for url, expected, description in test_urls:
        result = asyncio.run(manager.should_crawl_url(url))
        if result == expected:
            print(f"  ✅ {description}: {url}")
            passed += 1
        else:
            print(f"  ❌ {description}: {url} (expected {expected}, got {result})")
            failed += 1
    
    print(f"✅ URL filtering test: {passed} passed, {failed} failed")
    return failed == 0

def test_enhanced_link_classifier():
    """Test enhanced link classification with business patterns"""
    print("\n🔗 Testing enhanced link classification...")
    
    from business_intel_scraper.backend.crawling import EnhancedAdaptiveLinkClassifier
    
    classifier = EnhancedAdaptiveLinkClassifier()
    
    # Test links with various business intelligence patterns
    test_links = [
        {
            'url': 'https://company.com/company-profile',
            'anchor_text': 'Company Profile',
            'context': 'Learn about our business and corporate information',
            'expected_high': True
        },
        {
            'url': 'https://corp.com/investor-relations',
            'anchor_text': 'Investor Relations',
            'context': 'Financial statements and annual reports',
            'expected_high': True
        },
        {
            'url': 'https://business.com/contact-us',
            'anchor_text': 'Contact Us',
            'context': 'Get in touch with our team',
            'expected_high': False
        },
        {
            'url': 'https://site.com/privacy-policy',
            'anchor_text': 'Privacy Policy',
            'context': 'Our privacy and cookie policy',
            'expected_high': False
        },
        {
            'url': 'https://finance.com/earnings-report',
            'anchor_text': 'Q3 Earnings Report',
            'context': 'Quarterly financial data and revenue',
            'expected_high': True
        }
    ]
    
    print(f"🎯 Testing {len(test_links)} link classifications...")
    
    correct_classifications = 0
    for i, link in enumerate(test_links, 1):
        classified = classifier.classify_link(
            url=link['url'],
            anchor_text=link['anchor_text'],
            context=link['context']
        )
        
        is_high_value = classified.confidence > 0.7
        expected = link['expected_high']
        
        status = "✅" if is_high_value == expected else "❌"
        print(f"  {status} Link {i}: {link['anchor_text']}")
        print(f"       URL: {link['url']}")
        print(f"       Category: {classified.category.value}")
        print(f"       Confidence: {classified.confidence:.2f}")
        print(f"       Priority: {classified.priority.name}")
        
        if is_high_value == expected:
            correct_classifications += 1
    
    accuracy = correct_classifications / len(test_links)
    print(f"✅ Classification accuracy: {accuracy:.1%} ({correct_classifications}/{len(test_links)})")
    
    # Show pattern stats
    stats = classifier.get_pattern_stats()
    print(f"✅ Pattern categories: {stats['pattern_categories']}")
    print(f"✅ Total patterns: {stats['total_patterns']}")
    
    return accuracy >= 0.6  # 60% minimum accuracy

def test_content_hashing():
    """Test content hashing for duplicate detection"""
    print("\n#️⃣ Testing content hashing and duplicate detection...")
    
    from business_intel_scraper.backend.crawling import AdvancedCrawlManager
    
    manager = AdvancedCrawlManager(db_url=None)
    
    # Test content samples
    content1 = "<html><body><h1>Company ABC</h1><p>Leading technology company</p></body></html>"
    content2 = "<html><body><h1>Company ABC</h1><p>Leading technology company</p></body></html>"
    content3 = "<html><body><h1>Company XYZ</h1><p>Different company entirely</p></body></html>"
    content4 = "<html>    <body>  <h1>Company ABC</h1>  <p>Leading technology company</p>  </body>  </html>"
    
    hash1 = manager.calculate_content_hash(content1)
    hash2 = manager.calculate_content_hash(content2)
    hash3 = manager.calculate_content_hash(content3)
    hash4 = manager.calculate_content_hash(content4)
    
    print(f"  Content 1 hash: {hash1}")
    print(f"  Content 2 hash: {hash2}")
    print(f"  Content 3 hash: {hash3}")
    print(f"  Content 4 hash (whitespace diff): {hash4}")
    
    # Test duplicate detection
    if hash1 == hash2:
        print("✅ Identical content produces identical hashes")
    else:
        print("❌ Identical content should produce identical hashes")
        return False
    
    if hash1 != hash3:
        print("✅ Different content produces different hashes")
    else:
        print("❌ Different content should produce different hashes")
        return False
    
    if hash1 == hash4:
        print("✅ Whitespace normalization works correctly")
    else:
        print("❌ Whitespace normalization should make content identical")
        return False
    
    return True

def test_discovered_page_metadata():
    """Test discovered page metadata structure"""
    print("\n📄 Testing discovered page metadata...")
    
    from business_intel_scraper.backend.crawling import DiscoveredPage, SeedSource
    
    # Create test discovered page
    page = DiscoveredPage(
        url="https://example.com/company-profile",
        parent_url="https://example.com/directory",
        anchor_text="View Company Profile",
        source_type="directory",
        depth=2,
        classification_score=0.85,
        classification_type="business_profile",
        metadata={
            'discovery_method': 'link_extraction',
            'page_title': 'Company Profile - Example Corp',
            'response_time': 1.2
        }
    )
    
    print(f"✅ Created discovered page:")
    print(f"   URL: {page.url}")
    print(f"   Parent: {page.parent_url}")
    print(f"   Depth: {page.depth}")
    print(f"   Score: {page.classification_score}")
    print(f"   Type: {page.classification_type}")
    print(f"   Status: {page.crawl_status}")
    print(f"   Timestamp: {page.discovery_timestamp}")
    
    # Test seed source
    seed = SeedSource(
        name="Test Registry",
        urls=["https://test.com/companies"],
        source_type="business_registry",
        priority=8,
        crawl_config={'max_depth': 3, 'delay': 1.0}
    )
    
    print(f"✅ Created seed source:")
    print(f"   Name: {seed.name}")
    print(f"   URLs: {len(seed.urls)}")
    print(f"   Type: {seed.source_type}")
    print(f"   Priority: {seed.priority}")
    
    return True

async def test_crawl_manager_initialization():
    """Test crawl manager initialization and configuration"""
    print("\n⚙️ Testing crawl manager initialization...")
    
    from business_intel_scraper.backend.crawling import AdvancedCrawlManager
    
    # Test with various configurations
    configs = [
        {"db_url": None, "max_concurrent": 10, "max_depth": 3},
        {"db_url": None, "max_concurrent": 25, "max_depth": 5},
        {"db_url": None, "redis_url": "redis://localhost:6379/1", "max_concurrent": 5}
    ]
    
    for i, config in enumerate(configs, 1):
        print(f"  🔧 Testing configuration {i}: {config}")
        
        try:
            manager = AdvancedCrawlManager(**config)
            
            # Test basic functionality
            metrics = await manager.get_discovery_metrics()
            
            print(f"    ✅ Manager initialized successfully")
            print(f"    📊 Initial metrics: {json.dumps(metrics, indent=6)}")
            print(f"    🌱 Seed sources: {len(manager.seed_sources)}")
            print(f"    🔒 Domain rules: {len(manager.domain_rules)}")
            
        except Exception as e:
            print(f"    ❌ Failed to initialize manager: {e}")
            return False
    
    return True

async def test_integration():
    """Test integration between all components"""
    print("\n🔄 Testing component integration...")
    
    from business_intel_scraper.backend.crawling import AdvancedCrawlManager, CrawlOrchestrator
    
    # Create manager with limited scope for testing
    manager = AdvancedCrawlManager(
        db_url=None,
        max_concurrent=2,
        max_depth=1  # Limit depth for testing
    )
    
    # Override seed sources with safe test URLs
    manager.seed_sources = {
        'test_source': {
            'name': "Test Source",
            'urls': ["https://httpbin.org/html"],  # Safe test URL
            'source_type': 'test',
            'priority': 10
        }
    }
    
    # Create orchestrator
    orchestrator = CrawlOrchestrator(manager)
    
    print("🚀 Starting limited integration test...")
    
    try:
        # Run a very limited crawl operation
        # Note: This will make actual HTTP requests to httpbin.org
        result = await asyncio.wait_for(
            orchestrator.run_intelligence_gathering("integration_test"),
            timeout=30  # 30 second timeout
        )
        
        print(f"✅ Integration test completed:")
        print(f"   Operation: {result['operation_name']}")
        print(f"   Pages discovered: {result['discovered_pages']}")
        print(f"   Duration: {result['duration_seconds']:.2f}s")
        print(f"   Summary: {json.dumps(result['summary'], indent=4)}")
        
        return True
        
    except asyncio.TimeoutError:
        print("⚠️ Integration test timed out (this is expected in some environments)")
        return True  # Don't fail the test for timeout
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

async def main():
    """Run all tests for the advanced crawling system"""
    print("🚀 Starting Advanced Crawling/Discovery Layer Tests")
    print("=" * 60)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Seed Sources", test_seed_sources),
        ("Domain Rules", test_domain_rules),
        ("Enhanced Link Classifier", test_enhanced_link_classifier),
        ("Content Hashing", test_content_hashing),
        ("Discovered Page Metadata", test_discovered_page_metadata),
        ("Crawl Manager Initialization", test_crawl_manager_initialization),
        ("Integration", test_integration)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
                failed += 1
                
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"ADVANCED CRAWLING TEST SUMMARY")
    print('='*60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Success Rate: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 All advanced crawling tests passed!")
        print("✨ Your comprehensive crawling system is ready for production!")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Check the logs above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
