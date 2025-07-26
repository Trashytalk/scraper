"""
Integration between automated source discovery and the spider marketplace
"""

import json
import asyncio
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path

from .automated_discovery import AutomatedDiscoveryManager, DiscoveredSource


class MarketplaceIntegration:
    """Integration between discovery system and marketplace"""

    def __init__(self, discovery_manager: AutomatedDiscoveryManager):
        self.discovery_manager = discovery_manager
        self.spider_templates_dir = (
            Path(__file__).parent.parent / "marketplace" / "templates"
        )
        self.generated_spiders_dir = (
            Path(__file__).parent.parent / "marketplace" / "generated"
        )

        # Ensure directories exist
        self.spider_templates_dir.mkdir(parents=True, exist_ok=True)
        self.generated_spiders_dir.mkdir(parents=True, exist_ok=True)

    async def auto_generate_spiders(
        self, min_confidence: float = 0.7, max_spiders: int = 10
    ) -> List[Dict[str, Any]]:
        """Automatically generate spiders from high-confidence discovered sources"""

        # Get validated high-confidence sources
        sources = self.discovery_manager.get_discovered_sources(
            status="validated", min_confidence=min_confidence
        )

        if not sources:
            return []

        generated_spiders = []

        for source in sources[:max_spiders]:
            try:
                spider_config = await self._generate_spider_config(source)
                spider_code = await self._generate_spider_code(source, spider_config)

                # Save spider
                spider_filename = f"{source.domain.replace('.', '_')}_spider.py"
                spider_path = self.generated_spiders_dir / spider_filename

                with open(spider_path, "w") as f:
                    f.write(spider_code)

                # Create marketplace entry
                marketplace_entry = {
                    "name": f"{source.domain.replace('.', '_')}_spider",
                    "display_name": f"{source.domain.title()} Business Intelligence Spider",
                    "description": f"Auto-generated spider for {source.domain} based on automated discovery",
                    "source_url": source.url,
                    "confidence_score": source.confidence_score,
                    "generated_at": datetime.utcnow().isoformat(),
                    "spider_type": self._determine_spider_type(source),
                    "categories": self._extract_categories(source),
                    "features": self._extract_features(source),
                    "file_path": str(spider_path),
                    "discovery_metadata": source.metadata,
                }

                generated_spiders.append(marketplace_entry)

            except Exception as e:
                print(f"Error generating spider for {source.url}: {e}")
                continue

        # Save marketplace catalog
        await self._update_marketplace_catalog(generated_spiders)

        return generated_spiders

    async def _generate_spider_config(self, source: DiscoveredSource) -> Dict[str, Any]:
        """Generate spider configuration based on discovered source"""

        config = {
            "name": f"{source.domain.replace('.', '_')}_spider",
            "allowed_domains": [source.domain],
            "start_urls": [source.url],
            "custom_settings": {
                "ROBOTSTXT_OBEY": True,
                "DOWNLOAD_DELAY": 2,
                "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
                "USER_AGENT": "Business Intelligence Scraper (+http://example.com/bot)",
            },
        }

        # Analyze source metadata for configuration
        if "api_endpoints" in source.metadata and source.metadata["api_endpoints"]:
            config["api_mode"] = True
            config["api_endpoints"] = source.metadata["api_endpoints"]

        if "forms" in source.metadata and source.metadata["forms"]:
            config["has_forms"] = True
            config["forms"] = source.metadata["forms"]

        if "login_required" in source.metadata:
            config["login_required"] = source.metadata["login_required"]

        # Determine extraction strategy
        if source.source_type == "government_data":
            config["extraction_strategy"] = "structured_data"
        elif source.source_type == "business_directory":
            config["extraction_strategy"] = "directory_listing"
        elif source.source_type == "news_site":
            config["extraction_strategy"] = "article_content"
        else:
            config["extraction_strategy"] = "general_business"

        return config

    async def _generate_spider_code(
        self, source: DiscoveredSource, config: Dict[str, Any]
    ) -> str:
        """Generate spider code based on source and configuration"""

        # Base spider template
        template = '''#!/usr/bin/env python3
"""
Auto-generated spider for {domain}
Generated by Business Intelligence Scraper Discovery System
Source: {source_url}
Confidence Score: {confidence_score:.2f}
Generated: {generated_at}
"""

import scrapy
from urllib.parse import urljoin, urlparse
from datetime import datetime
import re


class {class_name}(scrapy.Spider):
    name = "{spider_name}"
    allowed_domains = {allowed_domains}
    start_urls = {start_urls}
    
    custom_settings = {custom_settings}
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_metadata = {source_metadata}
    
    def parse(self, response):
        """Main parsing method - auto-generated based on discovery analysis"""
        
        # Extract basic page information
        yield {{
            'url': response.url,
            'domain': urlparse(response.url).netloc,
            'title': response.css('title::text').get(),
            'timestamp': datetime.utcnow().isoformat(),
            'spider_name': self.name,
            'page_type': 'main'
        }}
        
        {extraction_logic}
        
        {link_following_logic}
    
    {additional_methods}
'''

        # Generate class name
        domain_clean = source.domain.replace(".", "_").replace("-", "_")
        class_name = (
            "".join(word.capitalize() for word in domain_clean.split("_")) + "Spider"
        )

        # Generate extraction logic based on source type and metadata
        extraction_logic = self._generate_extraction_logic(source, config)

        # Generate link following logic
        link_following_logic = self._generate_link_following_logic(source, config)

        # Generate additional methods if needed
        additional_methods = self._generate_additional_methods(source, config)

        # Fill template
        spider_code = template.format(
            domain=source.domain,
            source_url=source.url,
            confidence_score=source.confidence_score,
            generated_at=datetime.utcnow().isoformat(),
            class_name=class_name,
            spider_name=config["name"],
            allowed_domains=config["allowed_domains"],
            start_urls=config["start_urls"],
            custom_settings=config["custom_settings"],
            source_metadata=json.dumps(source.metadata, indent=8),
            extraction_logic=extraction_logic,
            link_following_logic=link_following_logic,
            additional_methods=additional_methods,
        )

        return spider_code

    def _generate_extraction_logic(
        self, source: DiscoveredSource, config: Dict[str, Any]
    ) -> str:
        """Generate extraction logic based on source analysis"""

        logic = []

        # API-based extraction
        if config.get("api_mode"):
            logic.append(
                """
        # API endpoint extraction detected
        api_data = self.extract_api_data(response)
        if api_data:
            yield api_data"""
            )

        # Form-based extraction
        if config.get("has_forms"):
            logic.append(
                """
        # Form submission logic
        forms = response.css('form')
        for form in forms:
            yield self.handle_form_submission(form, response)"""
            )

        # Standard extraction based on source type
        if source.source_type == "business_directory":
            logic.append(
                """
        # Business directory extraction
        business_listings = response.css('.listing, .business-item, .directory-entry')
        for listing in business_listings:
            business_data = {
                'name': listing.css('.name, .title, h2, h3::text').get(),
                'address': listing.css('.address, .location::text').get(),
                'phone': listing.css('.phone, .tel::text').get(),
                'website': listing.css('a[href*="http"]::attr(href)').get(),
                'description': listing.css('.description, .summary::text').get(),
                'category': listing.css('.category, .type::text').get(),
                'source_url': response.url,
                'extracted_at': datetime.utcnow().isoformat()
            }
            if business_data['name']:
                yield business_data"""
            )

        elif source.source_type == "government_data":
            logic.append(
                """
        # Government data extraction
        data_tables = response.css('table, .data-table')
        for table in data_tables:
            headers = table.css('th::text').getall()
            rows = table.css('tr')[1:]  # Skip header row
            
            for row in rows:
                cells = row.css('td::text').getall()
                if len(cells) >= len(headers):
                    row_data = dict(zip(headers, cells))
                    row_data.update({
                        'source_url': response.url,
                        'data_type': 'government_record',
                        'extracted_at': datetime.utcnow().isoformat()
                    })
                    yield row_data"""
            )

        elif source.source_type == "news_site":
            logic.append(
                """
        # News article extraction
        articles = response.css('article, .article, .news-item')
        for article in articles:
            article_data = {
                'headline': article.css('h1, h2, .headline::text').get(),
                'author': article.css('.author, .byline::text').get(),
                'publish_date': article.css('.date, .published, time::text').get(),
                'content': ' '.join(article.css('p::text').getall()),
                'category': article.css('.category, .section::text').get(),
                'source_url': response.url,
                'article_type': 'news',
                'extracted_at': datetime.utcnow().isoformat()
            }
            if article_data['headline']:
                yield article_data"""
            )

        else:
            # Generic business intelligence extraction
            logic.append(
                """
        # Generic business intelligence extraction
        
        # Extract contact information
        emails = re.findall(r'[\\w\\.-]+@[\\w\\.-]+\\.\\w+', response.text)
        phones = re.findall(r'[\\(]?\\d{3}[\\)\\-\\.]?\\s?\\d{3}[\\-\\.]?\\d{4}', response.text)
        
        # Extract company information
        company_info = {
            'url': response.url,
            'title': response.css('title::text').get(),
            'description': response.css('meta[name="description"]::attr(content)').get(),
            'emails': emails[:5],  # Limit to first 5 emails
            'phones': phones[:3],  # Limit to first 3 phones
            'social_links': response.css('a[href*="facebook.com"], a[href*="twitter.com"], a[href*="linkedin.com"]::attr(href)').getall(),
            'extracted_at': datetime.utcnow().isoformat()
        }
        
        if any([company_info['emails'], company_info['phones']]):
            yield company_info"""
            )

        return (
            "\n        ".join(logic)
            if logic
            else "        # No specific extraction logic generated"
        )

    def _generate_link_following_logic(
        self, source: DiscoveredSource, config: Dict[str, Any]
    ) -> str:
        """Generate link following logic"""

        if config["extraction_strategy"] == "directory_listing":
            return """
        # Follow pagination and detail pages
        next_page = response.css('.pagination .next::attr(href), .next-page::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        
        # Follow individual business detail pages
        detail_links = response.css('.listing a::attr(href), .business-item a::attr(href)').getall()
        for link in detail_links[:10]:  # Limit concurrent requests
            yield response.follow(link, callback=self.parse_detail)"""

        elif config["extraction_strategy"] == "structured_data":
            return """
        # Follow data navigation links
        data_links = response.css('.data-nav a::attr(href), .dataset a::attr(href)').getall()
        for link in data_links[:5]:  # Conservative following for government sites
            yield response.follow(link, callback=self.parse)"""

        else:
            return """
        # Conservative link following for general sites
        internal_links = [
            link for link in response.css('a::attr(href)').getall() 
            if link and not link.startswith(('http://', 'https://'))
        ]
        for link in internal_links[:3]:  # Very conservative
            if any(keyword in link.lower() for keyword in ['about', 'services', 'products', 'contact']):
                yield response.follow(link, callback=self.parse)"""

    def _generate_additional_methods(
        self, source: DiscoveredSource, config: Dict[str, Any]
    ) -> str:
        """Generate additional methods if needed"""

        methods = []

        if config["extraction_strategy"] == "directory_listing":
            methods.append(
                '''
    def parse_detail(self, response):
        """Parse individual business detail pages"""
        detail_data = {
            'url': response.url,
            'name': response.css('h1::text, .business-name::text').get(),
            'full_address': response.css('.address, .location').get(),
            'description': response.css('.description, .about::text').get(),
            'hours': response.css('.hours, .opening-hours::text').get(),
            'services': response.css('.services li::text').getall(),
            'page_type': 'detail',
            'extracted_at': datetime.utcnow().isoformat()
        }
        
        if detail_data['name']:
            yield detail_data'''
            )

        if config.get("api_mode"):
            methods.append(
                '''
    def extract_api_data(self, response):
        """Extract data from API endpoints"""
        try:
            # Check if response contains JSON data
            if 'application/json' in response.headers.get('content-type', '').decode():
                data = response.json()
                return {
                    'api_data': data,
                    'source_url': response.url,
                    'data_type': 'api_response',
                    'extracted_at': datetime.utcnow().isoformat()
                }
        except Exception as e:
            self.logger.warning(f"Failed to parse API response: {e}")
        return None'''
            )

        if config.get("has_forms"):
            methods.append(
                '''
    def handle_form_submission(self, form, response):
        """Handle form submissions if needed"""
        # Placeholder for form handling logic
        # This would require careful consideration of form types
        return {
            'form_action': form.css('::attr(action)').get(),
            'form_method': form.css('::attr(method)').get(),
            'form_fields': form.css('input::attr(name)').getall(),
            'source_url': response.url,
            'data_type': 'form_analysis',
            'extracted_at': datetime.utcnow().isoformat()
        }'''
            )

        return "\n".join(methods)

    def _determine_spider_type(self, source: DiscoveredSource) -> str:
        """Determine spider type based on source analysis"""
        if source.source_type == "government_data":
            return "government"
        elif source.source_type == "business_directory":
            return "directory"
        elif source.source_type == "news_site":
            return "news"
        elif "api_endpoints" in source.metadata and source.metadata["api_endpoints"]:
            return "api"
        else:
            return "general"

    def _extract_categories(self, source: DiscoveredSource) -> List[str]:
        """Extract categories from source metadata"""
        categories = ["automated", source.source_type]

        # Add domain-based categories
        if "gov" in source.domain:
            categories.append("government")
        if any(
            word in source.domain.lower() for word in ["business", "company", "corp"]
        ):
            categories.append("business")
        if any(word in source.domain.lower() for word in ["news", "media", "press"]):
            categories.append("news")

        return list(set(categories))

    def _extract_features(self, source: DiscoveredSource) -> List[str]:
        """Extract features from source metadata"""
        features = []

        if "api_endpoints" in source.metadata and source.metadata["api_endpoints"]:
            features.append("api_integration")
        if "forms" in source.metadata and source.metadata["forms"]:
            features.append("form_submission")
        if source.confidence_score > 0.8:
            features.append("high_confidence")
        if "login_required" in source.metadata and not source.metadata.get(
            "login_required"
        ):
            features.append("no_auth_required")

        return features

    async def _update_marketplace_catalog(self, new_spiders: List[Dict[str, Any]]):
        """Update the marketplace catalog with new spiders"""

        catalog_file = self.generated_spiders_dir / "catalog.json"

        # Load existing catalog
        existing_catalog = []
        if catalog_file.exists():
            try:
                with open(catalog_file, "r") as f:
                    existing_catalog = json.load(f)
            except Exception as e:
                print(f"Error loading existing catalog: {e}")

        # Add new spiders (avoid duplicates)
        existing_names = {spider.get("name") for spider in existing_catalog}
        for spider in new_spiders:
            if spider["name"] not in existing_names:
                existing_catalog.append(spider)

        # Save updated catalog
        with open(catalog_file, "w") as f:
            json.dump(existing_catalog, f, indent=2)

        print(f"Updated marketplace catalog with {len(new_spiders)} new spiders")


async def demo_marketplace_integration():
    """Demo the marketplace integration"""
    print("🏪 Marketplace Integration Demo")
    print("=" * 50)

    # Initialize discovery manager
    discovery_manager = AutomatedDiscoveryManager()

    # Create marketplace integration
    marketplace = MarketplaceIntegration(discovery_manager)

    # Auto-generate spiders from discovered sources
    print("Generating spiders from discovered sources...")
    generated_spiders = await marketplace.auto_generate_spiders(
        min_confidence=0.6, max_spiders=3
    )

    if generated_spiders:
        print(f"\n✅ Generated {len(generated_spiders)} spiders:")
        for spider in generated_spiders:
            print(f"  • {spider['display_name']}")
            print(f"    Source: {spider['source_url']}")
            print(f"    Confidence: {spider['confidence_score']:.2f}")
            print(f"    Type: {spider['spider_type']}")
            print(f"    Categories: {', '.join(spider['categories'])}")
            print(f"    File: {spider['file_path']}")
            print()
    else:
        print("No high-confidence sources available for spider generation")

    print("Marketplace integration demo completed!")


if __name__ == "__main__":
    asyncio.run(demo_marketplace_integration())
