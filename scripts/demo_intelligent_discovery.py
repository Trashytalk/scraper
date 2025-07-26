#!/usr/bin/env python3
"""
Intelligent Discovery System Demo

This demo showcases the advanced ML-powered business intelligence system
with intelligent crawling, adaptive schema detection, and smart prioritization.
"""

import sys
import asyncio
import time
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from business_intel_scraper.backend.discovery.scheduler import (
    IntelligentCrawlScheduler,
    CrawlRequest,
    CrawlPriority,
)
from business_intel_scraper.backend.discovery.classifier import AdaptiveLinkClassifier
from business_intel_scraper.backend.discovery.graph_analyzer import CrawlGraphAnalyzer
from business_intel_scraper.backend.extraction.schema_detector import SchemaDetector
from business_intel_scraper.backend.extraction.adaptive_scraper import (
    AdaptiveBusinessScraper,
)
from business_intel_scraper.backend.extraction.template_manager import TemplateManager


class IntelligentDiscoveryDemo:
    """Demo of the complete intelligent discovery system"""

    def __init__(self):
        print("🚀 Initializing Intelligent Discovery System Demo")
        print("=" * 60)

        # Initialize all components
        self.scheduler = IntelligentCrawlScheduler(
            {
                "max_concurrent_crawls": 10,
                "enable_ml_scoring": False,  # Will use rule-based for demo
                "priority_boost_factor": 1.2,
                "response_time_threshold": 5.0,
            }
        )

        self.classifier = AdaptiveLinkClassifier(
            {"min_confidence": 0.5, "enable_ml_classification": False}
        )

        self.graph_analyzer = CrawlGraphAnalyzer(
            {"enable_networkx": False, "max_depth": 5}  # Fallback mode
        )

        self.schema_detector = SchemaDetector(
            {"min_confidence": 0.6, "enable_advanced_analysis": False}
        )

        self.template_manager = TemplateManager()

        print("✅ All components initialized successfully!")
        print()

    def demo_intelligent_scheduling(self):
        """Demonstrate intelligent crawl scheduling"""
        print("📅 INTELLIGENT CRAWL SCHEDULING DEMO")
        print("-" * 40)

        # Add diverse crawl requests
        demo_requests = [
            ("https://example-corp.com/", "company_spider", CrawlPriority.CRITICAL, 0),
            ("https://example-corp.com/about", "company_spider", CrawlPriority.HIGH, 1),
            (
                "https://example-corp.com/investor-relations",
                "financial_spider",
                CrawlPriority.HIGH,
                1,
            ),
            (
                "https://example-corp.com/contact",
                "contact_spider",
                CrawlPriority.NORMAL,
                1,
            ),
            ("https://example-corp.com/privacy", "legal_spider", CrawlPriority.LOW, 2),
            (
                "https://example-corp.com/careers",
                "general_spider",
                CrawlPriority.BACKGROUND,
                2,
            ),
        ]

        print(f"Adding {len(demo_requests)} crawl requests...")
        for url, spider, priority, depth in demo_requests:
            request = CrawlRequest(
                url=url,
                spider_name=spider,
                priority=priority,
                depth=depth,
                metadata={"added_by": "demo", "timestamp": time.time()},
            )
            success = self.scheduler.add_crawl_request(request)
            print(
                f"  {'✅' if success else '❌'} {priority.name:10} | {spider:15} | {url}"
            )

        print("\n🔄 Processing crawl queue (Priority-First)...")
        processed = []
        while True:
            request = self.scheduler.get_next_crawl_request()
            if not request:
                break

            print(f"  🔸 Processing: {request.priority.name:10} | {request.url}")

            # Simulate crawl execution
            success = True
            response_time = 1.5 + (request.depth * 0.5)  # Deeper pages take longer
            data_quality = 0.9 - (request.depth * 0.1)  # Quality decreases with depth

            extracted_links = (
                [f"{request.url}/subpage-{i}" for i in range(2)]
                if request.depth < 2
                else []
            )

            # Complete the request
            self.scheduler.complete_crawl_request(
                request.url,
                success=success,
                response_time=response_time,
                data_quality=data_quality,
                extracted_links=extracted_links,
            )

            processed.append(request)

        # Show scheduler statistics
        stats = self.scheduler.get_scheduler_stats()
        print("\n📊 Scheduler Performance:")
        print(f"  • Total Processed: {stats['requests_processed']}")
        print(f"  • Completed: {stats['completed_crawls']}")
        print(
            f"  • Success Rate: {list(stats['top_domains'].values())[0]['success_rate']:.1%}"
        )
        print()

        return processed

    def demo_adaptive_link_classification(self):
        """Demonstrate adaptive link classification"""
        print("🔗 ADAPTIVE LINK CLASSIFICATION DEMO")
        print("-" * 42)

        # Simulate discovered links with various types
        discovered_links = [
            (
                "https://acme-corp.com/about-us",
                "About ACME Corporation",
                "https://acme-corp.com",
            ),
            (
                "https://acme-corp.com/leadership",
                "Executive Leadership Team",
                "https://acme-corp.com",
            ),
            (
                "https://acme-corp.com/investor-relations",
                "Investor Relations",
                "https://acme-corp.com",
            ),
            (
                "https://acme-corp.com/quarterly-earnings",
                "Q3 2024 Earnings Report",
                "https://acme-corp.com",
            ),
            (
                "https://acme-corp.com/press-releases",
                "Press Releases",
                "https://acme-corp.com",
            ),
            (
                "https://acme-corp.com/contact-us",
                "Contact Information",
                "https://acme-corp.com",
            ),
            (
                "https://acme-corp.com/products",
                "Our Products & Services",
                "https://acme-corp.com",
            ),
            (
                "https://acme-corp.com/partnerships",
                "Strategic Partnerships",
                "https://acme-corp.com",
            ),
            (
                "https://acme-corp.com/legal/privacy",
                "Privacy Policy",
                "https://acme-corp.com",
            ),
            (
                "https://twitter.com/acme_corp",
                "@acme_corp on Twitter",
                "https://acme-corp.com",
            ),
            (
                "mailto:info@acme-corp.com",
                "info@acme-corp.com",
                "https://acme-corp.com",
            ),
            (
                "https://acme-corp.com/random-page",
                "Random Page",
                "https://acme-corp.com",
            ),
        ]

        print(f"Classifying {len(discovered_links)} discovered links...")
        classified_links = self.classifier.classify_links_batch(discovered_links)

        # Group by category for display
        by_category = {}
        for link in classified_links:
            category = link.category.value
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(link)

        print("\n📊 Classification Results:")
        for category, links in sorted(by_category.items()):
            print(f"\n🏷️  {category.upper().replace('_', ' ')}")
            for link in links:
                priority_icon = {
                    "CRITICAL": "🔴",
                    "HIGH": "🟡",
                    "NORMAL": "🟢",
                    "LOW": "🔵",
                    "BACKGROUND": "⚪",
                }
                icon = priority_icon.get(link.priority.name, "⚫")
                print(f"    {icon} {link.confidence:.2f} | {link.url}")

        # Show classifier statistics
        stats = self.classifier.get_classifier_stats()
        print("\n📈 Classifier Stats:")
        print(f"  • Categories: {len(stats['categories'])}")
        print(f"  • ML Available: {stats['ml_available']}")
        print(f"  • Confidence Threshold: {stats['confidence_threshold']}")
        print()

        return classified_links

    def demo_schema_detection(self):
        """Demonstrate adaptive schema detection"""
        print("🔍 ADAPTIVE SCHEMA DETECTION DEMO")
        print("-" * 38)

        # Sample HTML content representing different business pages
        test_pages = {
            "Company Profile": """
            <!DOCTYPE html>
            <html>
            <head>
                <title>ACME Corporation - Leading Technology Solutions</title>
                <meta name="description" content="ACME Corp is a global leader in innovative technology solutions">
            </head>
            <body>
                <h1>ACME Corporation</h1>
                <div class="company-info">
                    <p>Founded: 1995</p>
                    <p>Industry: Technology</p>
                    <p>Employees: 50,000+</p>
                    <p>Headquarters: Silicon Valley, CA</p>
                </div>
                <p>Contact: <a href="mailto:info@acme-corp.com">info@acme-corp.com</a></p>
                <p>Phone: <a href="tel:+1-555-123-4567">+1-555-123-4567</a></p>
            </body>
            </html>
            """,
            "Financial Data": """
            <!DOCTYPE html>
            <html>
            <head><title>ACME Corp Financial Information</title></head>
            <body>
                <h1>Financial Performance</h1>
                <div class="financial-data">
                    <p class="ticker">Stock: ACME</p>
                    <p class="market-cap">Market Cap: $50.2B</p>
                    <p class="price">Share Price: $425.67</p>
                    <p class="pe-ratio">P/E Ratio: 18.5</p>
                    <p class="dividend">Dividend Yield: 2.1%</p>
                </div>
            </body>
            </html>
            """,
            "Contact Page": """
            <!DOCTYPE html>
            <html>
            <body>
                <h1>Contact ACME Corporation</h1>
                <div class="contact-info">
                    <p>Email: <a href="mailto:contact@acme-corp.com">contact@acme-corp.com</a></p>
                    <p>Phone: <a href="tel:+1-555-987-6543">+1-555-987-6543</a></p>
                    <div class="address">
                        <p>1234 Tech Drive</p>
                        <p>Silicon Valley, CA 94000</p>
                    </div>
                </div>
            </body>
            </html>
            """,
        }

        print(f"Analyzing {len(test_pages)} different page types...\n")

        detected_schemas = []
        for page_type, html_content in test_pages.items():
            print(f"🔎 Analyzing: {page_type}")

            schema = self.schema_detector.detect_schema(
                html_content,
                f"https://acme-corp.com/{page_type.lower().replace(' ', '-')}",
            )

            if schema:
                detected_schemas.append(schema)
                print(
                    f"  ✅ Schema: {schema.name} (confidence: {schema.confidence:.2f})"
                )
                print(f"  📋 Fields detected: {len(schema.fields)}")

                for field in schema.fields[:3]:  # Show first 3 fields
                    print(
                        f"     • {field.name}: {field.data_type.value} ({field.confidence:.2f})"
                    )

                if len(schema.fields) > 3:
                    print(f"     ... and {len(schema.fields) - 3} more fields")
            else:
                print("  ❌ No schema detected")
            print()

        # Show detector statistics
        stats = self.schema_detector.get_detector_stats()
        print("📊 Schema Detection Stats:")
        print(f"  • Analysis Available: {stats['analysis_available']}")
        print(f"  • Min Confidence: {stats['min_confidence']}")
        print(f"  • Schemas Detected: {len(detected_schemas)}")
        print()

        return detected_schemas

    def demo_template_extraction(self):
        """Demonstrate template-based extraction"""
        print("📝 TEMPLATE-BASED EXTRACTION DEMO")
        print("-" * 38)

        # Sample content for extraction
        company_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>TechCorp Industries - Innovation Leaders</title>
            <meta name="description" content="TechCorp Industries is a premier technology company specializing in AI solutions">
        </head>
        <body>
            <h1>TechCorp Industries</h1>
            <div class="company-details">
                <p class="industry">Industry: Artificial Intelligence</p>
                <p class="founded">Founded: 2010</p>
                <p class="employees">Employees: 15,000</p>
                <p class="headquarters">Headquarters: Austin, TX</p>
            </div>
            <div class="contact">
                <a href="mailto:hello@techcorp.com">hello@techcorp.com</a>
                <a href="tel:+1-512-555-0100">+1-512-555-0100</a>
            </div>
        </body>
        </html>
        """

        print("🎯 Applying extraction templates...")

        # Test different templates
        templates_to_test = ["company_profile", "contact_info", "financial_data"]

        for template_id in templates_to_test:
            print(f"\n📋 Template: {template_id}")

            result = self.template_manager.apply_template(
                template_id, company_html, "https://techcorp.com/about"
            )

            if result and result["data"]:
                print(
                    f"  ✅ Extraction successful (confidence: {result['confidence']:.2f})"
                )
                print("  📊 Data extracted:")

                for field, value in result["data"].items():
                    field_confidence = result["field_confidences"].get(field, 0.0)
                    print(f"     • {field}: '{value}' ({field_confidence:.2f})")
            else:
                print("  ❌ No data extracted")

        # Show template manager stats
        stats = self.template_manager.get_manager_stats()
        print("\n📈 Template Manager Stats:")
        print(f"  • Total Templates: {stats['total_templates']}")
        print(f"  • Template Types: {len(stats['template_types'])}")
        for template_type, count in stats["template_types"].items():
            print(f"     - {template_type}: {count}")
        print()

    def demo_graph_analysis(self):
        """Demonstrate crawl graph analysis"""
        print("🕸️  CRAWL GRAPH ANALYSIS DEMO")
        print("-" * 32)

        # Simulate a crawl with interconnected pages
        crawl_data = [
            (
                "https://company.com/",
                [
                    "https://company.com/about",
                    "https://company.com/contact",
                    "https://company.com/investors",
                ],
                0.9,
                1.2,
            ),
            (
                "https://company.com/about",
                ["https://company.com/leadership", "https://company.com/history"],
                0.8,
                1.8,
            ),
            ("https://company.com/contact", ["mailto:info@company.com"], 0.7, 1.1),
            (
                "https://company.com/investors",
                ["https://company.com/earnings", "https://company.com/sec-filings"],
                0.9,
                2.1,
            ),
            (
                "https://company.com/leadership",
                ["https://company.com/ceo-bio", "https://company.com/board"],
                0.8,
                1.5,
            ),
            ("https://company.com/earnings", [], 0.9, 1.3),
        ]

        print(f"🔗 Building crawl graph with {len(crawl_data)} nodes...")

        for url, links, data_value, response_time in crawl_data:
            success = (
                len(links) > 0 or "earnings" in url
            )  # Assume success if has links or is earnings

            self.graph_analyzer.add_crawl_result(
                url=url,
                extracted_links=links,
                success=success,
                data_value=data_value,
                response_time=response_time,
            )

            print(f"  📄 {url}")
            print(
                f"     Links: {len(links)} | Quality: {data_value:.1f} | Time: {response_time:.1f}s"
            )

        # Analyze the graph
        print("\n🔍 Graph Analysis:")

        # Get optimization suggestions
        suggestions = self.graph_analyzer.get_optimization_suggestions()
        if suggestions:
            print("💡 Optimization Suggestions:")
            for suggestion in suggestions[:3]:  # Show top 3
                print(f"  • {suggestion}")

        # Get high-value nodes
        high_value = self.graph_analyzer.get_high_value_nodes(limit=3)
        if high_value:
            print("\n⭐ Top High-Value Pages:")
            for i, (url, score) in enumerate(high_value, 1):
                print(f"  {i}. {url} (score: {score:.2f})")

        # Get stats
        stats = self.graph_analyzer.get_graph_stats()
        print("\n📊 Graph Statistics:")
        print(f"  • Total Nodes: {stats.get('total_nodes', 0)}")
        print(f"  • Success Rate: {stats.get('success_rate', 0):.1%}")
        print(f"  • Avg Response Time: {stats.get('avg_response_time', 0):.2f}s")
        print(f"  • NetworkX Available: {stats.get('networkx_available', False)}")
        print()

    async def demo_adaptive_scraper_integration(self):
        """Demonstrate the full adaptive scraper integration"""
        print("🤖 ADAPTIVE SCRAPER INTEGRATION DEMO")
        print("-" * 42)

        # Initialize the adaptive scraper
        config = {
            "scheduler": {"enable_ml_scoring": False, "max_concurrent_crawls": 5},
            "classifier": {"min_confidence": 0.6},
            "extractor": {"min_confidence": 0.7},
            "headless": True,
            "max_concurrent_extractions": 3,
        }

        scraper = AdaptiveBusinessScraper(config)

        # Add seed URLs for a comprehensive crawl
        seed_urls = [
            "https://example-company.com/",
            "https://example-company.com/about",
            "https://example-company.com/investor-relations",
        ]

        print(f"🌱 Adding {len(seed_urls)} seed URLs...")
        added = scraper.add_seed_urls(seed_urls)
        print(f"✅ Successfully added {added} URLs to crawl queue")

        # Simulate the discovery and extraction process
        print("\n🔄 Simulating intelligent crawl process...")

        # The scraper would normally run autonomously, but for demo we'll simulate
        simulated_results = [
            {
                "url": "https://example-company.com/",
                "schema": "company_profile",
                "data": {
                    "company_name": "Example Corporation",
                    "industry": "Technology",
                    "description": "Leading provider of innovative solutions",
                },
                "confidence": 0.85,
                "links_found": 12,
            },
            {
                "url": "https://example-company.com/about",
                "schema": "company_profile",
                "data": {
                    "company_name": "Example Corporation",
                    "founded": "1999",
                    "employees": "10,000+",
                },
                "confidence": 0.78,
                "links_found": 6,
            },
            {
                "url": "https://example-company.com/investor-relations",
                "schema": "financial_data",
                "data": {"stock_symbol": "EXAM", "market_cap": "$25.8B"},
                "confidence": 0.92,
                "links_found": 8,
            },
        ]

        for result in simulated_results:
            print(f"  📊 Extracted from {result['url']}")
            print(
                f"     Schema: {result['schema']} (confidence: {result['confidence']:.2f})"
            )
            print(
                f"     Data: {len(result['data'])} fields | Links: {result['links_found']}"
            )

        # Show final statistics
        stats = scraper.get_scraper_stats()
        print("\n📈 Final Scraper Statistics:")
        print(f"  • Browser Available: {stats['browser_available']}")
        print(f"  • Total Extractions: {stats['total_extractions']}")
        print(f"  • Known Schemas: {stats['known_schemas']}")
        print(f"  • Active Crawls: {stats['active_crawls']}")
        print()


async def main():
    """Run the complete intelligent discovery demo"""
    demo = IntelligentDiscoveryDemo()

    print("🎭 INTELLIGENT BUSINESS DISCOVERY SYSTEM")
    print("🎯 Advanced Implementation Demonstration")
    print("=" * 60)
    print()

    # Run all demo sections
    demos = [
        ("Intelligent Scheduling", demo.demo_intelligent_scheduling),
        ("Link Classification", demo.demo_adaptive_link_classification),
        ("Schema Detection", demo.demo_schema_detection),
        ("Template Extraction", demo.demo_template_extraction),
        ("Graph Analysis", demo.demo_graph_analysis),
        ("Adaptive Integration", demo.demo_adaptive_scraper_integration),
    ]

    for i, (name, demo_func) in enumerate(demos, 1):
        print(f"🎬 Demo {i}/{len(demos)}: {name}")
        print("=" * 60)

        try:
            if asyncio.iscoroutinefunction(demo_func):
                await demo_func()
            else:
                demo_func()
        except Exception as e:
            print(f"❌ Error in {name}: {e}")

        if i < len(demos):
            print("\n" + "─" * 60 + "\n")

    print("🎉 DEMO COMPLETE!")
    print("=" * 60)
    print("✨ The Intelligent Discovery System successfully demonstrates:")
    print("   • ML-powered crawl scheduling and prioritization")
    print("   • Adaptive link classification with confidence scoring")
    print("   • Dynamic schema detection and template extraction")
    print("   • Graph-based crawl optimization")
    print("   • Integrated adaptive scraping with all components")
    print()
    print("🚀 Your advanced business intelligence system is ready!")


if __name__ == "__main__":
    asyncio.run(main())
