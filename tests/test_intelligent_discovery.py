#!/usr/bin/env python3
"""
Test Script for Intelligent Discovery System

This script tests the core components of our advanced implementation
without requiring all external dependencies.
"""

import sys
import asyncio
import json
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))


def test_basic_imports():
    """Test that our core modules can be imported"""
    print("🔧 Testing basic imports...")

    try:
        from business_intel_scraper.backend.discovery.scheduler import (
            IntelligentCrawlScheduler,
            CrawlRequest,
            CrawlPriority,
        )

        print("✅ IntelligentCrawlScheduler imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import scheduler: {e}")
        return False

    try:
        from business_intel_scraper.backend.discovery.classifier import (
            AdaptiveLinkClassifier,
            LinkInfo,
            LinkCategory,
        )

        print("✅ AdaptiveLinkClassifier imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import classifier: {e}")
        return False

    try:
        from business_intel_scraper.backend.discovery.graph_analyzer import (
            CrawlGraphAnalyzer,
        )

        print("✅ CrawlGraphAnalyzer imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import graph analyzer: {e}")
        return False

    try:
        from business_intel_scraper.backend.extraction.schema_detector import (
            SchemaDetector,
            DetectedSchema,
        )

        print("✅ SchemaDetector imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import schema detector: {e}")
        return False

    try:
        from business_intel_scraper.backend.extraction.adaptive_scraper import (
            AdaptiveBusinessScraper,
        )

        print("✅ AdaptiveBusinessScraper imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import adaptive scraper: {e}")
        return False

    return True


def test_scheduler():
    """Test the intelligent crawl scheduler"""
    print("\n📅 Testing IntelligentCrawlScheduler...")

    from business_intel_scraper.backend.discovery.scheduler import (
        IntelligentCrawlScheduler,
        CrawlRequest,
        CrawlPriority,
    )

    # Initialize scheduler
    config = {
        "max_concurrent_crawls": 5,
        "enable_ml_scoring": False,
    }  # Disable ML for basic test
    scheduler = IntelligentCrawlScheduler(config)

    # Add test requests
    test_urls = [
        "https://example.com/about",
        "https://example.com/contact",
        "https://example.com/products",
        "https://example.com/news",
    ]

    for i, url in enumerate(test_urls):
        request = CrawlRequest(
            url=url, spider_name="test_spider", priority=CrawlPriority.NORMAL, depth=i
        )
        success = scheduler.add_crawl_request(request)
        if not success:
            print(f"❌ Failed to add request: {url}")
            return False

    # Test request retrieval
    requests_retrieved = []
    while len(requests_retrieved) < len(test_urls):
        request = scheduler.get_next_crawl_request()
        if not request:
            break
        requests_retrieved.append(request)

    print(f"✅ Retrieved {len(requests_retrieved)} requests from scheduler")

    # Test completion
    for request in requests_retrieved:
        scheduler.complete_crawl_request(
            request.url,
            success=True,
            response_time=1.0,
            data_quality=0.8,
            extracted_links=["https://example.com/link1", "https://example.com/link2"],
        )

    # Get stats
    stats = scheduler.get_scheduler_stats()
    print(f"✅ Scheduler stats: {json.dumps(stats, indent=2)}")

    return True


def test_classifier():
    """Test the adaptive link classifier"""
    print("\n🔗 Testing AdaptiveLinkClassifier...")

    from business_intel_scraper.backend.discovery.classifier import (
        AdaptiveLinkClassifier,
    )

    # Initialize classifier
    classifier = AdaptiveLinkClassifier({"min_confidence": 0.5})

    # Test link classification
    test_links = [
        ("https://example.com/about-us", "About Us", "https://example.com"),
        ("https://example.com/contact", "Contact Information", "https://example.com"),
        (
            "https://example.com/investor-relations",
            "Investor Relations",
            "https://example.com",
        ),
        ("https://example.com/privacy-policy", "Privacy Policy", "https://example.com"),
        ("mailto:contact@example.com", "contact@example.com", "https://example.com"),
    ]

    classified_links = classifier.classify_links_batch(test_links)

    for link_info in classified_links:
        print(
            f"✅ Classified: {link_info.url} -> {link_info.category.value} (confidence: {link_info.confidence:.2f}, priority: {link_info.priority.name})"
        )

    # Get stats
    stats = classifier.get_classifier_stats()
    print(f"✅ Classifier stats: {json.dumps(stats, indent=2)}")

    return True


def test_schema_detector():
    """Test the schema detector"""
    print("\n🔍 Testing SchemaDetector...")

    from business_intel_scraper.backend.extraction.schema_detector import SchemaDetector

    # Initialize detector
    detector = SchemaDetector({"min_confidence": 0.5})

    # Test HTML for schema detection
    test_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Example Company - About Us</title>
        <meta name="description" content="Example Company is a leading technology firm">
    </head>
    <body>
        <h1>Example Company</h1>
        <p>Contact us at: info@example.com</p>
        <p>Phone: (555) 123-4567</p>
        <p>Address: 123 Main St, City, State 12345</p>
        <a href="https://example.com/products">Our Products</a>
    </body>
    </html>
    """

    # Detect schema
    schema = detector.detect_schema(test_html, "https://example.com/about")

    if schema:
        print(
            f"✅ Detected schema: {schema.name} (confidence: {schema.confidence:.2f})"
        )
        print(f"   Fields detected: {len(schema.fields)}")
        for field in schema.fields:
            print(
                f"     - {field.name}: {field.data_type.value} (confidence: {field.confidence:.2f})"
            )
    else:
        print("❌ No schema detected")
        return False

    # Get stats
    stats = detector.get_detector_stats()
    print(f"✅ Detector stats: {json.dumps(stats, indent=2)}")

    return True


async def test_adaptive_scraper():
    """Test the adaptive business scraper"""
    print("\n🤖 Testing AdaptiveBusinessScraper...")

    from business_intel_scraper.backend.extraction.adaptive_scraper import (
        AdaptiveBusinessScraper,
    )

    # Initialize scraper
    config = {
        "scheduler": {"enable_ml_scoring": False},
        "headless": True,
        "max_concurrent_extractions": 2,
    }
    scraper = AdaptiveBusinessScraper(config)

    # Add seed URLs (using example.com for testing)
    seed_urls = [
        "https://httpbin.org/html",  # Simple HTML for testing
        "https://httpbin.org/json",  # JSON response
    ]

    added = scraper.add_seed_urls(seed_urls)
    print(f"✅ Added {added} seed URLs")

    # Get initial stats
    stats = scraper.get_scraper_stats()
    print("✅ Initial scraper stats:")
    print(f"   Total extractions: {stats['total_extractions']}")
    print(f"   Known schemas: {stats['known_schemas']}")
    print(f"   Browser available: {stats['browser_available']}")

    # For testing, we'll simulate a small crawl without actually making HTTP requests
    print("✅ Adaptive scraper initialized successfully")

    return True


def test_integration():
    """Test integration between components"""
    print("\n🔄 Testing component integration...")

    from business_intel_scraper.backend.discovery.scheduler import (
        IntelligentCrawlScheduler,
        CrawlRequest,
    )
    from business_intel_scraper.backend.discovery.classifier import (
        AdaptiveLinkClassifier,
    )
    from business_intel_scraper.backend.discovery.graph_analyzer import (
        CrawlGraphAnalyzer,
    )

    # Initialize components
    scheduler = IntelligentCrawlScheduler({"enable_ml_scoring": False})
    classifier = AdaptiveLinkClassifier()
    analyzer = CrawlGraphAnalyzer()

    # Simulate crawl workflow
    # 1. Add initial request
    request = CrawlRequest(url="https://example.com", spider_name="test")
    scheduler.add_crawl_request(request)

    # 2. Get request
    active_request = scheduler.get_next_crawl_request()
    if not active_request:
        print("❌ No request retrieved from scheduler")
        return False

    # 3. Simulate link discovery and classification
    discovered_links = [
        ("https://example.com/about", "About", "https://example.com"),
        ("https://example.com/contact", "Contact", "https://example.com"),
    ]

    classified_links = classifier.classify_links_batch(discovered_links)
    print(f"✅ Classified {len(classified_links)} discovered links")

    # 4. Update graph analyzer
    analyzer.add_crawl_result(
        url="https://example.com",
        extracted_links=[link[0] for link in discovered_links],
        success=True,
        data_value=0.8,
        response_time=1.5,
    )

    # 5. Complete request in scheduler
    scheduler.complete_crawl_request(
        "https://example.com",
        success=True,
        response_time=1.5,
        data_quality=0.8,
        extracted_links=[link[0] for link in discovered_links],
    )

    print("✅ Integration test completed successfully")
    return True


async def main():
    """Run all tests"""
    print("🚀 Starting Intelligent Discovery System Tests\n")

    tests = [
        ("Basic Imports", test_basic_imports),
        ("Scheduler", test_scheduler),
        ("Classifier", test_classifier),
        ("Schema Detector", test_schema_detector),
        ("Adaptive Scraper", test_adaptive_scraper),
        ("Integration", test_integration),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print("=" * 50)

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

    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Success Rate: {passed/(passed+failed)*100:.1f}%")

    if failed == 0:
        print("\n🎉 All tests passed! Intelligent Discovery System is ready.")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Check the logs above.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
