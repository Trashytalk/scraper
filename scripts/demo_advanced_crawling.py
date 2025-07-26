#!/usr/bin/env python3
"""
Advanced Crawling System Demo (Dependency-Free Version)

This demo shows how the advanced crawling/discovery layer would work
without requiring additional dependencies. It simulates the crawling
process and demonstrates all the key features.
"""

import sys
import asyncio
import re
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple
from urllib.parse import urlparse
from collections import defaultdict

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

print("🚀 ADVANCED CRAWLING/DISCOVERY LAYER DEMONSTRATION")
print("=" * 60)
print()


class MockDiscoveredPage:
    """Mock version of discovered page for demonstration"""

    def __init__(
        self,
        url,
        parent_url=None,
        anchor_text=None,
        depth=0,
        classification_score=0.5,
        classification_type="unknown",
        source_type="unknown",
        metadata=None,
    ):
        self.url = url
        self.parent_url = parent_url
        self.anchor_text = anchor_text
        self.depth = depth
        self.classification_score = classification_score
        self.classification_type = classification_type
        self.source_type = source_type
        self.crawl_status = "discovered"
        self.discovery_timestamp = datetime.utcnow()
        self.page_hash = None
        self.metadata = metadata or {}


class MockSeedSource:
    """Mock version of seed source for demonstration"""

    def __init__(self, name, urls, source_type, priority=5):
        self.name = name
        self.urls = urls
        self.source_type = source_type
        self.priority = priority
        self.update_frequency = "daily"


class AdvancedCrawlingDemo:
    """Demonstration of advanced crawling capabilities"""

    def __init__(self):
        self.seed_sources = self._load_demo_seed_sources()
        self.domain_rules = self._load_demo_domain_rules()
        self.business_patterns = self._compile_business_patterns()
        self.discovered_pages = []
        self.crawled_urls = set()
        self.metrics = defaultdict(int)

    def _load_demo_seed_sources(self) -> Dict:
        """Load demonstration seed sources"""
        return {
            "business_registries": MockSeedSource(
                name="Business Registries",
                urls=[
                    "https://opencorpdata.com/companies",
                    "https://sec.gov/edgar/browse",
                    "https://dnb.com/business-directory",
                ],
                source_type="business_registry",
                priority=10,
            ),
            "industry_directories": MockSeedSource(
                name="Industry Directories",
                urls=[
                    "https://yellowpages.com/business-listings",
                    "https://manta.com/companies",
                    "https://bizapedia.com/directory",
                ],
                source_type="directory",
                priority=8,
            ),
            "financial_sites": MockSeedSource(
                name="Financial Information Sites",
                urls=[
                    "https://finance.yahoo.com/companies",
                    "https://bloomberg.com/companies",
                    "https://reuters.com/business/companies",
                ],
                source_type="financial",
                priority=9,
            ),
        }

    def _load_demo_domain_rules(self) -> Dict:
        """Load demonstration domain rules"""
        return {
            "allowed_domains": [
                "sec.gov",
                "opencorpdata.com",
                "dnb.com",
                "manta.com",
                "bizapedia.com",
                "yellowpages.com",
                "bloomberg.com",
                "yahoo.com",
                "reuters.com",
                "crunchbase.com",
            ],
            "blocked_domains": [
                "facebook.com",
                "twitter.com",
                "instagram.com",
                "youtube.com",
                "tiktok.com",
                "pinterest.com",
            ],
            "rate_limits": {
                "default": 1.0,
                "sec.gov": 5.0,
                "bloomberg.com": 3.0,
                "reuters.com": 2.5,
            },
            "url_patterns": {
                "include": [
                    r"/company/",
                    r"/business/",
                    r"/profile/",
                    r"/organization/",
                    r"/directory/",
                    r"/listing/",
                    r"/filing/",
                    r"/quote/",
                ],
                "exclude": [
                    r"/login",
                    r"/signup",
                    r"/register",
                    r"/cart",
                    r"/checkout",
                    r"/privacy",
                    r"/terms",
                    r"/cookie",
                    r"/help",
                    r"/support",
                ],
            },
        }

    def _compile_business_patterns(self) -> Dict:
        """Compile business intelligence patterns"""
        return {
            "high_value": [
                r"company[-_]profile",
                r"business[-_]profile",
                r"executive[-_]team",
                r"financial[-_]statements",
                r"annual[-_]report",
                r"investor[-_]relations",
            ],
            "medium_value": [
                r"contact[-_]us",
                r"company[-_]info",
                r"business[-_]directory",
                r"leadership",
                r"press[-_]release",
            ],
            "navigation": [
                r"next[-_]page",
                r"more[-_]results",
                r"view[-_]all",
                r"page[-_]\d+",
            ],
            "exclude": [
                r"login",
                r"signup",
                r"privacy[-_]policy",
                r"terms",
                r"careers",
            ],
        }

    def demo_seed_source_management(self):
        """Demonstrate seed source management"""
        print("🌱 SEED SOURCE MANAGEMENT DEMO")
        print("-" * 40)

        total_urls = 0
        for source_name, source in self.seed_sources.items():
            print(f"📂 {source.name}")
            print(f"   Type: {source.source_type}")
            print(f"   Priority: {source.priority}")
            print(f"   URLs: {len(source.urls)}")
            for url in source.urls[:2]:  # Show first 2 URLs
                print(f"     • {url}")
            if len(source.urls) > 2:
                print(f"     ... and {len(source.urls) - 2} more")
            total_urls += len(source.urls)
            print()

        print(f"✅ Total seed URLs configured: {total_urls}")
        print()

    def demo_domain_filtering(self):
        """Demonstrate domain and URL pattern filtering"""
        print("🔍 DOMAIN FILTERING & URL PATTERN MATCHING DEMO")
        print("-" * 50)

        test_urls = [
            ("https://sec.gov/edgar/company/apple-inc", True, "SEC company filing"),
            (
                "https://facebook.com/company/apple",
                False,
                "Blocked social media domain",
            ),
            (
                "https://bloomberg.com/company/profile/apple",
                True,
                "Financial site company profile",
            ),
            ("https://example.com/login", False, "Excluded login page"),
            (
                "https://manta.com/business/directory/apple-corp",
                True,
                "Business directory listing",
            ),
            ("https://youtube.com/watch?v=abc123", False, "Blocked video platform"),
            (
                "https://crunchbase.com/organization/apple",
                True,
                "Business intelligence platform",
            ),
        ]

        print("Testing URL filtering rules:")
        passed = 0

        for url, expected, description in test_urls:
            result = self.should_crawl_url(url)
            status = "✅" if result == expected else "❌"
            print(f"  {status} {description}")
            print(f"      URL: {url}")
            print(f"      Expected: {expected}, Got: {result}")
            if result == expected:
                passed += 1
            print()

        print(
            f"✅ URL Filtering Accuracy: {passed}/{len(test_urls)} ({passed/len(test_urls)*100:.1f}%)"
        )
        print()

    def demo_link_classification(self):
        """Demonstrate enhanced link classification"""
        print("🔗 ENHANCED LINK CLASSIFICATION DEMO")
        print("-" * 42)

        test_links = [
            {
                "url": "https://company.com/company-profile",
                "anchor_text": "Company Profile",
                "context": "Learn about our business operations and corporate structure",
            },
            {
                "url": "https://corp.com/investor-relations",
                "anchor_text": "Investor Relations",
                "context": "Financial statements, earnings reports, and SEC filings",
            },
            {
                "url": "https://business.com/annual-report-2024",
                "anchor_text": "Annual Report 2024",
                "context": "Our comprehensive annual financial report",
            },
            {
                "url": "https://site.com/contact-us",
                "anchor_text": "Contact Us",
                "context": "Get in touch with our customer service team",
            },
            {
                "url": "https://example.com/privacy-policy",
                "anchor_text": "Privacy Policy",
                "context": "Our privacy and cookie policy information",
            },
            {
                "url": "https://directory.com/next-page",
                "anchor_text": "Next Page",
                "context": "View more business listings",
            },
        ]

        print("Classifying discovered links:")
        high_value_count = 0

        for i, link in enumerate(test_links, 1):
            score, classification = self.classify_link(
                link["url"], link["anchor_text"], link["context"]
            )

            if score > 0.7:
                priority = "🔴 CRITICAL"
                high_value_count += 1
            elif score > 0.5:
                priority = "🟡 HIGH"
            elif score > 0.3:
                priority = "🟢 MEDIUM"
            else:
                priority = "🔵 LOW"

            print(f"  📄 Link {i}: {link['anchor_text']}")
            print(f"      URL: {link['url']}")
            print(f"      Classification: {classification}")
            print(f"      Score: {score:.2f}")
            print(f"      Priority: {priority}")
            print()

        print(f"✅ High-value links identified: {high_value_count}/{len(test_links)}")
        print()

    def demo_content_deduplication(self):
        """Demonstrate content hashing and duplicate detection"""
        print("🔄 CONTENT DEDUPLICATION DEMO")
        print("-" * 34)

        # Simulate different page contents
        content_samples = [
            (
                "Page 1",
                "<html><body><h1>ACME Corp</h1><p>Technology leader</p></body></html>",
            ),
            (
                "Page 2",
                "<html><body><h1>ACME Corp</h1><p>Technology leader</p></body></html>",
            ),
            (
                "Page 3",
                "<html>  <body>  <h1>ACME Corp</h1>  <p>Technology leader</p>  </body>  </html>",
            ),
            (
                "Page 4",
                "<html><body><h1>XYZ Inc</h1><p>Different company</p></body></html>",
            ),
            (
                "Page 5",
                "<html><body><h1>ACME Corp</h1><p>Leading technology company</p></body></html>",
            ),
        ]

        hashes = {}
        duplicates_found = 0

        print("Computing content hashes:")
        for name, content in content_samples:
            content_hash = self.calculate_content_hash(content)
            hashes[name] = content_hash
            print(f"  {name}: {content_hash}")

            # Check for duplicates
            duplicate_of = None
            for other_name, other_hash in hashes.items():
                if other_name != name and other_hash == content_hash:
                    duplicate_of = other_name
                    duplicates_found += 1
                    break

            if duplicate_of:
                print(f"    ⚠️  Duplicate of {duplicate_of}")
            print()

        print(f"✅ Duplicate detection: {duplicates_found} duplicates found")
        print()

    def demo_crawl_scheduling(self):
        """Demonstrate intelligent crawl scheduling"""
        print("📅 INTELLIGENT CRAWL SCHEDULING DEMO")
        print("-" * 42)

        # Simulate discovered pages with different priorities
        discovered_pages = [
            MockDiscoveredPage(
                url="https://sec.gov/edgar/company/apple",
                source_type="business_registry",
                classification_score=0.95,
                classification_type="high_value_business",
                depth=0,
            ),
            MockDiscoveredPage(
                url="https://bloomberg.com/company/apple-profile",
                source_type="financial",
                classification_score=0.88,
                classification_type="financial_data",
                depth=1,
            ),
            MockDiscoveredPage(
                url="https://manta.com/business/apple-inc",
                source_type="directory",
                classification_score=0.72,
                classification_type="business_profile",
                depth=2,
            ),
            MockDiscoveredPage(
                url="https://example.com/contact",
                source_type="directory",
                classification_score=0.35,
                classification_type="contact_info",
                depth=2,
            ),
            MockDiscoveredPage(
                url="https://site.com/privacy",
                source_type="directory",
                classification_score=0.15,
                classification_type="exclude",
                depth=3,
            ),
        ]

        # Sort by priority (score descending, depth ascending)
        sorted_pages = sorted(
            discovered_pages, key=lambda p: (-p.classification_score, p.depth)
        )

        print("Crawl queue (priority order):")
        for i, page in enumerate(sorted_pages, 1):
            priority = self.get_priority_label(page.classification_score)
            print(
                f"  {i}. {priority} | Depth {page.depth} | Score {page.classification_score:.2f}"
            )
            print(f"     {page.url}")
            print(f"     Type: {page.classification_type} | Source: {page.source_type}")
            print()

        print("✅ Pages scheduled in optimal priority order")
        print()

    def demo_metadata_extraction(self):
        """Demonstrate metadata extraction and storage"""
        print("📊 METADATA EXTRACTION DEMO")
        print("-" * 32)

        # Simulate crawled pages with rich metadata
        sample_pages = [
            {
                "url": "https://sec.gov/edgar/company/apple-inc",
                "classification_score": 0.92,
                "classification_type": "regulatory_filing",
                "source_type": "business_registry",
                "depth": 1,
                "metadata": {
                    "content_type": "text/html",
                    "content_length": 45623,
                    "response_time": 1.2,
                    "status_code": 200,
                    "page_title": "Apple Inc - SEC Filings",
                    "last_modified": "2024-01-15T10:30:00Z",
                    "company_ticker": "AAPL",
                    "filing_types": ["10-K", "10-Q", "8-K"],
                },
            },
            {
                "url": "https://bloomberg.com/company/apple-financial-data",
                "classification_score": 0.89,
                "classification_type": "financial_data",
                "source_type": "financial",
                "depth": 2,
                "metadata": {
                    "content_type": "text/html",
                    "content_length": 32156,
                    "response_time": 0.8,
                    "status_code": 200,
                    "page_title": "Apple Inc Financial Overview",
                    "market_cap": "$2.8T",
                    "stock_price": "$175.43",
                    "pe_ratio": "28.5",
                },
            },
        ]

        print("Extracted metadata from crawled pages:")
        for page in sample_pages:
            print(f"📄 {page['url']}")
            print(
                f"   Classification: {page['classification_type']} (score: {page['classification_score']:.2f})"
            )
            print(f"   Source: {page['source_type']} | Depth: {page['depth']}")
            print(
                f"   Response: {page['metadata']['status_code']} | Time: {page['metadata']['response_time']}s"
            )
            print(f"   Content: {page['metadata']['content_length']} bytes")

            # Show domain-specific metadata
            if "company_ticker" in page["metadata"]:
                print(f"   Company Ticker: {page['metadata']['company_ticker']}")
            if "market_cap" in page["metadata"]:
                print(f"   Market Cap: {page['metadata']['market_cap']}")
                print(f"   Stock Price: {page['metadata']['stock_price']}")
            print()

        print("✅ Rich metadata extracted and stored for analysis")
        print()

    def demo_crawl_metrics(self):
        """Demonstrate comprehensive crawl metrics"""
        print("📈 COMPREHENSIVE CRAWL METRICS DEMO")
        print("-" * 40)

        # Simulate crawl operation metrics
        mock_metrics = {
            "runtime_seconds": 1847,
            "pages_crawled": 2456,
            "links_discovered": 18732,
            "active_crawlers": 0,
            "queue_size": 0,
            "crawl_rate_per_minute": 79.8,
            "high_value_pages": 387,
            "medium_value_pages": 1024,
            "low_value_pages": 1045,
            "errors": {"crawler_errors": 23, "crawl_errors": 156, "timeouts": 67},
            "top_domains": [
                {"domain": "sec.gov", "page_count": 445, "avg_score": 0.89},
                {"domain": "bloomberg.com", "page_count": 332, "avg_score": 0.84},
                {"domain": "reuters.com", "page_count": 298, "avg_score": 0.78},
                {"domain": "manta.com", "page_count": 267, "avg_score": 0.65},
                {"domain": "yellowpages.com", "page_count": 201, "avg_score": 0.58},
            ],
            "source_distribution": {
                "business_registry": 756,
                "financial": 623,
                "directory": 897,
                "forum": 180,
            },
        }

        print("📊 Crawl Operation Summary:")
        print(
            f"   ⏱️  Runtime: {mock_metrics['runtime_seconds']//60}m {mock_metrics['runtime_seconds']%60}s"
        )
        print(f"   📄 Pages Crawled: {mock_metrics['pages_crawled']:,}")
        print(f"   🔗 Links Discovered: {mock_metrics['links_discovered']:,}")
        print(
            f"   ⚡ Crawl Rate: {mock_metrics['crawl_rate_per_minute']:.1f} pages/min"
        )
        print()

        print("🎯 Quality Distribution:")
        total_quality = (
            mock_metrics["high_value_pages"]
            + mock_metrics["medium_value_pages"]
            + mock_metrics["low_value_pages"]
        )
        print(
            f"   🔴 High Value: {mock_metrics['high_value_pages']} ({mock_metrics['high_value_pages']/total_quality*100:.1f}%)"
        )
        print(
            f"   🟡 Medium Value: {mock_metrics['medium_value_pages']} ({mock_metrics['medium_value_pages']/total_quality*100:.1f}%)"
        )
        print(
            f"   🔵 Low Value: {mock_metrics['low_value_pages']} ({mock_metrics['low_value_pages']/total_quality*100:.1f}%)"
        )
        print()

        print("🌐 Top Domains by Page Count:")
        for domain in mock_metrics["top_domains"]:
            print(
                f"   {domain['domain']}: {domain['page_count']} pages (avg score: {domain['avg_score']:.2f})"
            )
        print()

        print("📂 Source Type Distribution:")
        for source_type, count in mock_metrics["source_distribution"].items():
            print(f"   {source_type}: {count} pages")
        print()

        error_rate = (
            sum(mock_metrics["errors"].values()) / mock_metrics["pages_crawled"] * 100
        )
        print(
            f"⚠️  Error Rate: {error_rate:.1f}% ({sum(mock_metrics['errors'].values())} errors)"
        )
        print()

    # Helper methods
    def should_crawl_url(self, url: str) -> bool:
        """Check if URL should be crawled based on domain and pattern rules"""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()

        # Check allowed domains
        if not any(
            allowed_domain in domain
            for allowed_domain in self.domain_rules["allowed_domains"]
        ):
            return False

        # Check blocked domains
        if any(
            blocked_domain in domain
            for blocked_domain in self.domain_rules["blocked_domains"]
        ):
            return False

        # Check URL patterns
        url_lower = url.lower()

        # Check exclude patterns first
        if any(
            re.search(pattern, url_lower)
            for pattern in self.domain_rules["url_patterns"]["exclude"]
        ):
            return False

        return True

    def classify_link(
        self, url: str, anchor_text: str, context: str
    ) -> Tuple[float, str]:
        """Classify link and return score and classification"""
        score = 0.0
        classification = "unknown"

        all_text = f"{url} {anchor_text} {context}".lower()

        # Check high-value patterns
        high_value_matches = sum(
            1
            for pattern in self.business_patterns["high_value"]
            if re.search(pattern, all_text)
        )
        if high_value_matches > 0:
            score += 0.8
            classification = "high_value_business"

        # Check medium-value patterns
        medium_value_matches = sum(
            1
            for pattern in self.business_patterns["medium_value"]
            if re.search(pattern, all_text)
        )
        if medium_value_matches > 0:
            score += 0.5
            if classification == "unknown":
                classification = "medium_value_business"

        # Check navigation patterns
        nav_matches = sum(
            1
            for pattern in self.business_patterns["navigation"]
            if re.search(pattern, anchor_text)
        )
        if nav_matches > 0:
            score += 0.3
            if classification == "unknown":
                classification = "navigation"

        # Check exclude patterns
        exclude_matches = sum(
            1
            for pattern in self.business_patterns["exclude"]
            if re.search(pattern, all_text)
        )
        if exclude_matches > 0:
            score -= 0.6
            classification = "exclude"

        return max(0.0, min(1.0, score)), classification

    def calculate_content_hash(self, content: str) -> str:
        """Calculate normalized content hash"""
        normalized = re.sub(r"\s+", " ", content.lower().strip())
        return hashlib.md5(normalized.encode()).hexdigest()[
            :12
        ]  # Shortened for display

    def get_priority_label(self, score: float) -> str:
        """Get priority label based on classification score"""
        if score >= 0.8:
            return "🔴 CRITICAL"
        elif score >= 0.6:
            return "🟡 HIGH"
        elif score >= 0.4:
            return "🟢 MEDIUM"
        elif score >= 0.2:
            return "🔵 LOW"
        else:
            return "⚫ IGNORE"


async def main():
    """Run the advanced crawling demonstration"""
    demo = AdvancedCrawlingDemo()

    print("🎭 This demonstration shows how the Advanced Crawling/Discovery Layer")
    print("   implements the detailed best-practice pipeline with:")
    print("   • Seed-based crawling with business intelligence sources")
    print("   • Recursive crawling with intelligent depth control")
    print("   • Domain and pattern-based URL filtering")
    print("   • Enhanced link classification with business patterns")
    print("   • Content deduplication with normalized hashing")
    print("   • Priority-based crawl scheduling")
    print("   • Rich metadata extraction and storage")
    print("   • Comprehensive metrics and monitoring")
    print()
    print("=" * 60)
    print()

    # Run all demonstrations
    demos = [
        demo.demo_seed_source_management,
        demo.demo_domain_filtering,
        demo.demo_link_classification,
        demo.demo_content_deduplication,
        demo.demo_crawl_scheduling,
        demo.demo_metadata_extraction,
        demo.demo_crawl_metrics,
    ]

    for demo_func in demos:
        demo_func()
        await asyncio.sleep(0.1)  # Small delay for readability

    print("🎉 ADVANCED CRAWLING DEMONSTRATION COMPLETE!")
    print("=" * 60)
    print("✨ Key Benefits Demonstrated:")
    print("   🎯 Intelligent source prioritization and seed management")
    print("   🔍 Smart URL filtering prevents crawling irrelevant content")
    print("   🧠 ML-ready link classification for business intelligence")
    print("   ⚡ Efficient duplicate detection saves bandwidth and storage")
    print("   📊 Rich metadata extraction enables deep business analysis")
    print("   📈 Comprehensive metrics provide operational visibility")
    print()
    print("🚀 Your advanced crawling system is ready for business intelligence!")


if __name__ == "__main__":
    asyncio.run(main())
