#!/usr/bin/env python3
"""
CLI commands for managing automated source discovery
"""

import asyncio
import sys
import argparse
import json

from ..discovery.automated_discovery import AutomatedDiscoveryManager


def setup_discovery_parser(subparsers):
    """Setup discovery command parser"""
    parser = subparsers.add_parser(
        "discovery", help="Manage automated source discovery"
    )

    discovery_subparsers = parser.add_subparsers(
        dest="discovery_command", help="Discovery commands"
    )

    # Run discovery command
    run_parser = discovery_subparsers.add_parser("run", help="Run source discovery")
    run_parser.add_argument("--urls", nargs="*", help="Seed URLs for discovery")
    run_parser.add_argument("--config", help="JSON config for discovery bots")
    run_parser.add_argument("--output", help="Output file for discovered sources")

    # List sources command
    list_parser = discovery_subparsers.add_parser(
        "list", help="List discovered sources"
    )
    list_parser.add_argument(
        "--status",
        choices=["candidate", "validated", "failed"],
        help="Filter by source status",
    )
    list_parser.add_argument(
        "--min-confidence", type=float, default=0.0, help="Minimum confidence score"
    )
    list_parser.add_argument(
        "--output-format",
        choices=["table", "json"],
        default="table",
        help="Output format",
    )

    # Validate sources command
    validate_parser = discovery_subparsers.add_parser(
        "validate", help="Validate discovered sources"
    )
    validate_parser.add_argument("--urls", nargs="*", help="Specific URLs to validate")
    validate_parser.add_argument(
        "--all", action="store_true", help="Validate all candidate sources"
    )

    # Generate spiders command
    generate_parser = discovery_subparsers.add_parser(
        "generate", help="Generate spiders from discovered sources"
    )
    generate_parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.7,
        help="Minimum confidence score for spider generation",
    )
    generate_parser.add_argument(
        "--template",
        choices=["scrapy", "playwright", "requests"],
        default="scrapy",
        help="Spider template to use",
    )


async def run_discovery_command(args):
    """Execute source discovery"""
    print("🔍 Starting automated source discovery...")

    # Default seed URLs if none provided
    seed_urls = (
        args.urls
        if args.urls
        else [
            "https://www.usa.gov/business",
            "https://www.gov.uk/browse/business",
            "https://europa.eu/youreurope/business/",
            "https://www.canada.ca/en/services/business.html",
        ]
    )

    # Load configuration
    config = {}
    if args.config:
        try:
            with open(args.config, "r") as f:
                config = json.load(f)
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            return False

    # Initialize discovery manager
    manager = AutomatedDiscoveryManager(config)

    try:
        # Run discovery
        sources = await manager.discover_sources(seed_urls)

        print(f"✅ Discovery completed! Found {len(sources)} sources")

        # Summary statistics
        high_confidence = [s for s in sources if s.confidence_score > 0.7]
        medium_confidence = [s for s in sources if 0.4 <= s.confidence_score <= 0.7]

        print(f"   📈 High confidence (>0.7): {len(high_confidence)} sources")
        print(f"   📊 Medium confidence (0.4-0.7): {len(medium_confidence)} sources")
        print(
            f"   📉 Lower confidence (<0.4): {len(sources) - len(high_confidence) - len(medium_confidence)} sources"
        )

        # Output to file if requested
        if args.output:
            output_data = [
                {
                    "url": s.url,
                    "domain": s.domain,
                    "title": s.title,
                    "description": s.description,
                    "source_type": s.source_type,
                    "confidence_score": s.confidence_score,
                    "discovered_at": s.discovered_at.isoformat(),
                    "metadata": s.metadata,
                }
                for s in sources
            ]

            with open(args.output, "w") as f:
                json.dump(output_data, f, indent=2)
            print(f"💾 Results saved to {args.output}")

        # Show top sources
        if high_confidence:
            print("\n🏆 Top discovered sources:")
            for source in sorted(
                high_confidence, key=lambda x: x.confidence_score, reverse=True
            )[:5]:
                print(f"   • {source.url} (confidence: {source.confidence_score:.2f})")
                if source.title:
                    print(f"     Title: {source.title}")
                if source.description:
                    print(f"     Description: {source.description[:100]}...")
                print()

        return True

    except Exception as e:
        print(f"❌ Discovery failed: {e}")
        return False


def list_sources_command(args):
    """List discovered sources"""
    manager = AutomatedDiscoveryManager()

    # Get sources with filters
    sources = manager.get_discovered_sources(
        status=args.status, min_confidence=args.min_confidence
    )

    if not sources:
        print("No sources found matching criteria")
        return True

    if args.output_format == "json":
        # JSON output
        output_data = [
            {
                "url": s.url,
                "domain": s.domain,
                "title": s.title,
                "source_type": s.source_type,
                "confidence_score": s.confidence_score,
                "status": s.status,
                "discovered_at": s.discovered_at.isoformat(),
            }
            for s in sources
        ]
        print(json.dumps(output_data, indent=2))
    else:
        # Table output
        print(f"\n📋 Found {len(sources)} discovered sources:")
        print("-" * 120)
        print(
            f"{'URL':<50} {'Domain':<25} {'Type':<15} {'Confidence':<10} {'Status':<10}"
        )
        print("-" * 120)

        for source in sorted(sources, key=lambda x: x.confidence_score, reverse=True):
            url_display = (
                source.url[:47] + "..." if len(source.url) > 50 else source.url
            )
            domain_display = (
                source.domain[:22] + "..." if len(source.domain) > 25 else source.domain
            )

            print(
                f"{url_display:<50} {domain_display:<25} {source.source_type:<15} "
                f"{source.confidence_score:<10.2f} {source.status:<10}"
            )

    return True


async def validate_sources_command(args):
    """Validate discovered sources"""
    print("✅ Validating sources...")

    manager = AutomatedDiscoveryManager()

    if args.urls:
        # Validate specific URLs
        validated_count = 0
        for url in args.urls:
            try:
                if await manager.validate_source(url):
                    print(f"✅ Validated: {url}")
                    validated_count += 1
                else:
                    print(f"❌ Failed: {url}")
            except Exception as e:
                print(f"❌ Error validating {url}: {e}")

        print(f"\n📊 Validated {validated_count}/{len(args.urls)} sources")

    elif args.all:
        # Validate all candidate sources
        candidate_sources = manager.get_discovered_sources(status="candidate")

        if not candidate_sources:
            print("No candidate sources to validate")
            return True

        print(f"Validating {len(candidate_sources)} candidate sources...")
        validated_count = 0

        for source in candidate_sources:
            try:
                if await manager.validate_source(source.url):
                    validated_count += 1
                    print(f"✅ Validated: {source.url}")
                else:
                    print(f"❌ Failed: {source.url}")
            except Exception as e:
                print(f"❌ Error validating {source.url}: {e}")

        print(
            f"\n📊 Validation complete: {validated_count}/{len(candidate_sources)} sources validated"
        )

    else:
        print("❌ Please specify --urls or --all")
        return False

    return True


def generate_spiders_command(args):
    """Generate spiders from discovered sources"""
    print("🕷️  Generating spiders from high-confidence sources...")

    manager = AutomatedDiscoveryManager()

    # Get high-confidence sources
    sources = manager.get_discovered_sources(
        status="validated", min_confidence=args.min_confidence
    )

    if not sources:
        print(f"No validated sources found with confidence >= {args.min_confidence}")
        return True

    print(f"Found {len(sources)} sources suitable for spider generation")

    # Generate spiders (simplified version for demo)
    spider_templates = {
        "scrapy": """
import scrapy

class {class_name}Spider(scrapy.Spider):
    name = "{spider_name}"
    allowed_domains = ["{domain}"]
    start_urls = ["{url}"]
    
    def parse(self, response):
        # Extract data based on discovered patterns
        {extraction_logic}
        
        yield {{
            'url': response.url,
            'title': response.css('title::text').get(),
            # Add more fields based on source analysis
        }}
""",
        "playwright": """
import asyncio
from playwright.async_api import async_playwright

class {class_name}Spider:
    def __init__(self):
        self.start_urls = ["{url}"]
        self.domain = "{domain}"
    
    async def scrape(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            await page.goto("{url}")
            
            # Extract data based on discovered patterns
            {extraction_logic}
            
            data = {{
                'url': page.url,
                'title': await page.title(),
                # Add more fields based on source analysis
            }}
            
            await browser.close()
            return data
""",
        "requests": """
import requests
from bs4 import BeautifulSoup

class {class_name}Spider:
    def __init__(self):
        self.start_urls = ["{url}"]
        self.domain = "{domain}"
    
    def scrape(self):
        session = requests.Session()
        
        for url in self.start_urls:
            try:
                response = session.get(url)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract data based on discovered patterns
                {extraction_logic}
                
                yield {{
                    'url': url,
                    'title': soup.title.get_text() if soup.title else None,
                    # Add more fields based on source analysis
                }}
                
            except Exception as e:
                print(f"Error scraping {{url}}: {{e}}")
""",
    }

    for i, source in enumerate(sources[:5]):  # Limit to 5 spiders for demo
        # Generate spider class name
        domain_clean = source.domain.replace(".", "_").replace("-", "_")
        class_name = "".join(word.capitalize() for word in domain_clean.split("_"))
        spider_name = f"{source.domain.replace('.', '_')}_spider"

        # Generate extraction logic based on source metadata
        extraction_logic = "# Automated extraction logic\n        "
        if "api_endpoints" in source.metadata:
            extraction_logic += "# API endpoints discovered: " + ", ".join(
                source.metadata["api_endpoints"][:3]
            )
        elif "forms" in source.metadata and source.metadata["forms"]:
            extraction_logic += "# Forms detected - consider form submission logic"
        else:
            extraction_logic += "# Use standard HTML parsing for data extraction"

        # Fill template
        template = spider_templates[args.template]
        spider_code = template.format(
            class_name=class_name,
            spider_name=spider_name,
            domain=source.domain,
            url=source.url,
            extraction_logic=extraction_logic,
        )

        # Save spider file
        filename = f"{spider_name}.py"
        with open(filename, "w") as f:
            f.write(spider_code)

        print(f"📄 Generated spider: {filename}")
        print(f"   Domain: {source.domain}")
        print(f"   Confidence: {source.confidence_score:.2f}")
        print(f"   Template: {args.template}")
        print()

    print(f"🎉 Spider generation complete! Generated {min(len(sources), 5)} spiders")
    return True


def main():
    """Main CLI entry point for discovery commands"""
    parser = argparse.ArgumentParser(description="Automated Source Discovery CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    setup_discovery_parser(subparsers)

    args = parser.parse_args()

    if not hasattr(args, "discovery_command") or args.discovery_command is None:
        parser.print_help()
        return False

    # Route to appropriate handler
    if args.discovery_command == "run":
        return asyncio.run(run_discovery_command(args))
    elif args.discovery_command == "list":
        return list_sources_command(args)
    elif args.discovery_command == "validate":
        return asyncio.run(validate_sources_command(args))
    elif args.discovery_command == "generate":
        return generate_spiders_command(args)
    else:
        print(f"Unknown discovery command: {args.discovery_command}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
