"""
Automated Source Discovery System
Implements intelligent discovery bots for finding and validating new data sources
"""

import asyncio
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class DiscoveredSource:
    """Represents a discovered data source"""

    url: str
    source_type: str = "unknown"
    region: str = "global"
    sector: str = "general"
    status: str = "candidate"
    confidence_score: float = 0.0
    discovery_method: str = "unknown"
    last_checked: datetime = field(default_factory=datetime.utcnow)
    extraction_notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    schema_version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "url": self.url,
            "source_type": self.source_type,
            "region": self.region,
            "sector": self.sector,
            "status": self.status,
            "confidence_score": self.confidence_score,
            "discovery_method": self.discovery_method,
            "last_checked": self.last_checked.isoformat(),
            "extraction_notes": self.extraction_notes,
            "metadata": self.metadata,
            "schema_version": self.schema_version,
        }


class SourceDiscoveryBot:
    """Base class for automated source discovery bots"""

    def __init__(self, bot_name: str, config: Optional[Dict] = None):
        self.bot_name = bot_name
        self.config = config or {}
        self.discovered_sources: List[DiscoveredSource] = []
        self.session: Optional[aiohttp.ClientSession] = None

        # Business intelligence keywords
        self.bi_keywords = {
            "high_value": [
                "business registry",
                "company register",
                "corporate directory",
                "procurement",
                "tender",
                "contract award",
                "business license",
                "trade registry",
                "export directory",
                "supplier database",
                "business association",
                "chamber commerce",
                "industry directory",
            ],
            "medium_value": [
                "business listing",
                "company database",
                "member directory",
                "professional services",
                "vendor list",
                "partner network",
                "business news",
                "industry report",
                "market research",
            ],
            "indicators": [
                "register",
                "registry",
                "directory",
                "database",
                "portal",
                "listing",
                "search",
                "browse",
                "members",
                "companies",
            ],
        }

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"User-Agent": "BusinessIntelligenceBot/1.0"},
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def discover_sources(self, seed_urls: List[str]) -> List[DiscoveredSource]:
        """Main discovery method to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement discover_sources")

    def score_source_relevance(self, url: str, content: str, title: str = "") -> float:
        """Score the relevance of a discovered source for business intelligence"""
        score = 0.0
        text_content = (content + " " + title + " " + url).lower()

        # High value keywords
        for keyword in self.bi_keywords["high_value"]:
            if keyword in text_content:
                score += 0.15

        # Medium value keywords
        for keyword in self.bi_keywords["medium_value"]:
            if keyword in text_content:
                score += 0.08

        # General indicators
        for indicator in self.bi_keywords["indicators"]:
            if indicator in text_content:
                score += 0.03

        # Domain-based scoring
        domain = urlparse(url).netloc.lower()
        if any(ext in domain for ext in [".gov", ".org", ".mil"]):
            score += 0.2
        elif any(ext in domain for ext in [".com", ".net"]):
            score += 0.05

        # URL structure scoring
        path = urlparse(url).path.lower()
        if any(
            term in path for term in ["directory", "registry", "database", "search"]
        ):
            score += 0.1

        return min(score, 1.0)  # Cap at 1.0


class DomainScannerBot(SourceDiscoveryBot):
    """Bot for scanning domains and discovering business registries"""

    def __init__(self, config: Optional[Dict] = None):
        super().__init__("domain_scanner", config)
        self.search_patterns = [
            "business registry {region}",
            "company register {region}",
            "trade directory {region}",
            "procurement portal {region}",
            "business association {region}",
            "chamber of commerce {region}",
        ]

    async def discover_sources(self, seed_urls: List[str]) -> List[DiscoveredSource]:
        """Discover sources by scanning domains and following high-value links"""
        discovered = []

        for seed_url in seed_urls:
            try:
                sources = await self._scan_domain(seed_url)
                discovered.extend(sources)
                await asyncio.sleep(1)  # Rate limiting
            except Exception as e:
                logger.error(f"Error scanning domain {seed_url}: {e}")

        return discovered

    async def _scan_domain(self, url: str) -> List[DiscoveredSource]:
        """Scan a single domain for business intelligence sources"""
        sources = []

        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    return sources

                content = await response.text()
                soup = BeautifulSoup(content, "html.parser")

                # Extract all links
                links = soup.find_all("a", href=True)

                for link in links:
                    href = link.get("href")
                    text = link.get_text(strip=True)

                    if not href:
                        continue

                    # Make absolute URL
                    absolute_url = urljoin(url, href)

                    # Skip non-HTTP links
                    if not absolute_url.startswith(("http://", "https://")):
                        continue

                    # Score the link
                    score = self.score_source_relevance(absolute_url, text)

                    if score > 0.3:  # Threshold for relevance
                        source = DiscoveredSource(
                            url=absolute_url,
                            source_type=self._classify_source_type(absolute_url, text),
                            confidence_score=score,
                            discovery_method="domain_scan",
                            extraction_notes=f"Link text: {text[:100]}",
                            metadata={
                                "parent_url": url,
                                "link_text": text,
                                "discovery_timestamp": datetime.utcnow().isoformat(),
                            },
                        )
                        sources.append(source)

        except Exception as e:
            logger.error(f"Error scanning domain {url}: {e}")

        return sources

    def _classify_source_type(self, url: str, text: str) -> str:
        """Classify the type of source based on URL and link text"""
        combined = (url + " " + text).lower()

        if any(term in combined for term in ["registry", "register"]):
            return "registry"
        elif any(term in combined for term in ["directory", "listing"]):
            return "directory"
        elif any(term in combined for term in ["procurement", "tender"]):
            return "procurement"
        elif any(term in combined for term in ["news", "press", "announcement"]):
            return "news"
        else:
            return "general"


class SearchEngineBot(SourceDiscoveryBot):
    """Bot for discovering sources via search engine APIs"""

    def __init__(self, config: Optional[Dict] = None):
        super().__init__("search_engine", config)
        self.api_key = config.get("google_api_key") if config else None
        self.search_engine_id = (
            config.get("google_search_engine_id") if config else None
        )
        self.regions = config.get(
            "target_regions", ["global", "us", "uk", "eu", "asia"]
        )

    async def discover_sources(self, seed_urls: List[str]) -> List[DiscoveredSource]:
        """Discover sources using search engine APIs"""
        if not self.api_key or not self.search_engine_id:
            logger.warning("Google API credentials not configured for SearchEngineBot")
            return []

        discovered = []

        for region in self.regions:
            for pattern in self._get_search_patterns():
                query = pattern.format(region=region)
                try:
                    sources = await self._search_google(query, region)
                    discovered.extend(sources)
                    await asyncio.sleep(2)  # Rate limiting for API
                except Exception as e:
                    logger.error(f"Error searching for '{query}': {e}")

        return discovered

    def _get_search_patterns(self) -> List[str]:
        """Get search patterns for finding business intelligence sources"""
        return [
            "business registry {region} site:gov",
            "company register {region} official",
            "trade directory {region} database",
            "procurement portal {region} government",
            "business license directory {region}",
            "export import database {region}",
            "chamber commerce member directory {region}",
            "professional association directory {region}",
        ]

    async def _search_google(self, query: str, region: str) -> List[DiscoveredSource]:
        """Search Google Custom Search API"""
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.api_key,
            "cx": self.search_engine_id,
            "q": query,
            "num": 10,
        }

        sources = []

        try:
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(f"Google Search API returned status {response.status}")
                    return sources

                data = await response.json()

                for item in data.get("items", []):
                    url = item.get("link")
                    title = item.get("title", "")
                    snippet = item.get("snippet", "")

                    score = self.score_source_relevance(url, snippet + " " + title)

                    if score > 0.2:  # Lower threshold for search results
                        source = DiscoveredSource(
                            url=url,
                            source_type=self._classify_source_type(
                                url, title + " " + snippet
                            ),
                            region=region,
                            confidence_score=score,
                            discovery_method="search_engine",
                            extraction_notes=f"Title: {title}, Snippet: {snippet[:100]}",
                            metadata={
                                "search_query": query,
                                "title": title,
                                "snippet": snippet,
                                "discovery_timestamp": datetime.utcnow().isoformat(),
                            },
                        )
                        sources.append(source)

        except Exception as e:
            logger.error(f"Error in Google search: {e}")

        return sources


class HeuristicAnalyzerBot(SourceDiscoveryBot):
    """Bot for analyzing discovered sources with business-specific heuristics"""

    def __init__(self, config: Optional[Dict] = None):
        super().__init__("heuristic_analyzer", config)

    async def discover_sources(self, seed_urls: List[str]) -> List[DiscoveredSource]:
        """Analyze sources using advanced heuristics"""
        analyzed_sources = []

        for url in seed_urls:
            try:
                source = await self._analyze_source(url)
                if source:
                    analyzed_sources.append(source)
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error analyzing source {url}: {e}")

        return analyzed_sources

    async def _analyze_source(self, url: str) -> Optional[DiscoveredSource]:
        """Perform detailed analysis of a source"""
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    return None

                content = await response.text()
                soup = BeautifulSoup(content, "html.parser")

                # Extract metadata
                title = soup.find("title")
                title_text = title.get_text(strip=True) if title else ""

                # Look for structured data indicators
                structured_indicators = self._find_structured_data_indicators(soup)

                # Analyze content for business intelligence value
                content_score = self._analyze_content_quality(content, soup)

                # Check for API endpoints
                api_endpoints = self._find_potential_apis(soup, url)

                # Calculate comprehensive score
                base_score = self.score_source_relevance(url, content, title_text)
                structure_bonus = len(structured_indicators) * 0.1
                api_bonus = len(api_endpoints) * 0.15

                total_score = min(base_score + structure_bonus + api_bonus, 1.0)

                if total_score > 0.3:  # Threshold for inclusion
                    return DiscoveredSource(
                        url=url,
                        source_type=self._classify_advanced_source_type(soup, url),
                        sector=self._identify_sector(content, title_text),
                        region=self._identify_region(content, url),
                        confidence_score=total_score,
                        discovery_method="heuristic_analysis",
                        extraction_notes=f"Title: {title_text}",
                        metadata={
                            "structured_indicators": structured_indicators,
                            "api_endpoints": api_endpoints,
                            "content_quality_score": content_score,
                            "page_title": title_text,
                            "discovery_timestamp": datetime.utcnow().isoformat(),
                        },
                    )

        except Exception as e:
            logger.error(f"Error analyzing source {url}: {e}")

        return None

    def _find_structured_data_indicators(self, soup: BeautifulSoup) -> List[str]:
        """Find indicators of structured data on the page"""
        indicators = []

        # Look for tables
        if soup.find_all("table"):
            indicators.append("data_tables")

        # Look for forms
        if soup.find_all("form"):
            indicators.append("search_forms")

        # Look for pagination
        if any(term in str(soup).lower() for term in ["next", "previous", "page"]):
            indicators.append("pagination")

        # Look for JSON-LD structured data
        json_ld = soup.find_all("script", type="application/ld+json")
        if json_ld:
            indicators.append("json_ld")

        return indicators

    def _analyze_content_quality(self, content: str, soup: BeautifulSoup) -> float:
        """Analyze the quality and structure of content"""
        score = 0.0

        # Content length indicator
        if len(content) > 5000:
            score += 0.2
        elif len(content) > 1000:
            score += 0.1

        # Number of links (indicates it's a directory/portal)
        links = soup.find_all("a", href=True)
        if len(links) > 50:
            score += 0.3
        elif len(links) > 20:
            score += 0.2

        # Presence of search functionality
        search_inputs = soup.find_all("input", {"type": "search"}) or soup.find_all(
            "input", {"name": re.compile(r"search", re.I)}
        )
        if search_inputs:
            score += 0.2

        return min(score, 1.0)

    def _find_potential_apis(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Find potential API endpoints"""
        endpoints = []

        # Look for common API paths in links
        api_patterns = [r"/api/", r"/v\d+/", r"\.json", r"\.xml", r"/rest/"]

        for link in soup.find_all("a", href=True):
            href = link.get("href")
            for pattern in api_patterns:
                if re.search(pattern, href, re.I):
                    absolute_url = urljoin(base_url, href)
                    endpoints.append(absolute_url)
                    break

        return list(set(endpoints))  # Remove duplicates

    def _classify_advanced_source_type(self, soup: BeautifulSoup, url: str) -> str:
        """Advanced classification of source type"""
        content_text = soup.get_text().lower()

        # Business registry patterns
        if any(
            term in content_text
            for term in ["business registration", "company registration", "incorporate"]
        ):
            return "business_registry"

        # Procurement patterns
        if any(
            term in content_text for term in ["tender", "rfp", "procurement", "bid"]
        ):
            return "procurement_portal"

        # Directory patterns
        if any(
            term in content_text
            for term in ["member directory", "business directory", "company listing"]
        ):
            return "business_directory"

        # News/announcements
        if any(
            term in content_text for term in ["news", "press release", "announcement"]
        ):
            return "news_portal"

        return "general_business"

    def _identify_sector(self, content: str, title: str) -> str:
        """Identify the business sector"""
        combined = (content + " " + title).lower()

        sector_keywords = {
            "finance": ["bank", "financial", "insurance", "investment"],
            "healthcare": ["health", "medical", "hospital", "pharmaceutical"],
            "technology": ["tech", "software", "it", "digital"],
            "manufacturing": ["manufacturing", "industrial", "factory"],
            "government": ["government", "public", "municipal", "federal"],
            "trade": ["import", "export", "trade", "customs"],
        }

        for sector, keywords in sector_keywords.items():
            if any(keyword in combined for keyword in keywords):
                return sector

        return "general"

    def _identify_region(self, content: str, url: str) -> str:
        """Identify the geographical region"""
        combined = (content + " " + url).lower()

        # Country/region patterns
        region_patterns = {
            "us": ["united states", "usa", ".gov", "america"],
            "uk": ["united kingdom", "britain", ".gov.uk"],
            "eu": ["european", "europa.eu"],
            "canada": ["canada", ".gc.ca"],
            "australia": ["australia", ".gov.au"],
            "singapore": ["singapore", ".gov.sg"],
            "uae": ["emirates", "dubai", "abu dhabi"],
        }

        for region, patterns in region_patterns.items():
            if any(pattern in combined for pattern in patterns):
                return region

        return "global"


class SourceRegistry:
    """Registry for managing discovered sources"""

    def __init__(self, storage_path: str = "data/discovered_sources.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.sources: Dict[str, DiscoveredSource] = {}
        self.load_sources()

    def load_sources(self) -> None:
        """Load sources from storage"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                    for url, source_data in data.items():
                        # Convert timestamp back to datetime
                        source_data["last_checked"] = datetime.fromisoformat(
                            source_data["last_checked"]
                        )
                        self.sources[url] = DiscoveredSource(**source_data)
            except Exception as e:
                logger.error(f"Error loading sources: {e}")

    def save_sources(self) -> None:
        """Save sources to storage"""
        try:
            data = {url: source.to_dict() for url, source in self.sources.items()}
            with open(self.storage_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving sources: {e}")

    def add_source(self, source: DiscoveredSource) -> None:
        """Add a discovered source to the registry"""
        existing = self.sources.get(source.url)
        if existing:
            # Update if new source has higher confidence or newer timestamp
            if (
                source.confidence_score > existing.confidence_score
                or source.last_checked > existing.last_checked
            ):
                self.sources[source.url] = source
        else:
            self.sources[source.url] = source

    def get_sources_by_criteria(
        self,
        source_type: Optional[str] = None,
        region: Optional[str] = None,
        sector: Optional[str] = None,
        min_confidence: float = 0.0,
    ) -> List[DiscoveredSource]:
        """Get sources matching criteria"""
        filtered = []
        for source in self.sources.values():
            if source_type and source.source_type != source_type:
                continue
            if region and source.region != region:
                continue
            if sector and source.sector != sector:
                continue
            if source.confidence_score < min_confidence:
                continue
            filtered.append(source)

        return sorted(filtered, key=lambda x: x.confidence_score, reverse=True)

    def mark_source_validated(self, url: str, status: str = "validated") -> None:
        """Mark a source as validated"""
        if url in self.sources:
            self.sources[url].status = status
            self.sources[url].last_checked = datetime.utcnow()


class AutomatedDiscoveryManager:
    """Main manager for automated source discovery operations"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.registry = SourceRegistry()
        self.bots: List[SourceDiscoveryBot] = []

        # Initialize bots based on configuration
        self._initialize_bots()

    def _initialize_bots(self) -> None:
        """Initialize discovery bots based on configuration"""
        bot_configs = self.config.get("bots", {})

        # Always include domain scanner and heuristic analyzer
        self.bots.extend(
            [
                DomainScannerBot(bot_configs.get("domain_scanner", {})),
                HeuristicAnalyzerBot(bot_configs.get("heuristic_analyzer", {})),
            ]
        )

        # Add search engine bot if API keys are provided
        search_config = bot_configs.get("search_engine", {})
        if search_config.get("google_api_key"):
            self.bots.append(SearchEngineBot(search_config))

    async def discover_sources(self, seed_urls: List[str]) -> List[DiscoveredSource]:
        """Run discovery operation using all configured bots"""
        all_sources = []

        for bot in self.bots:
            logger.info(f"Running discovery bot: {bot.bot_name}")
            try:
                async with bot:
                    sources = await bot.discover_sources(seed_urls)
                    all_sources.extend(sources)
                    logger.info(f"Bot {bot.bot_name} discovered {len(sources)} sources")
            except Exception as e:
                logger.error(f"Error running bot {bot.bot_name}: {e}")

        # Deduplicate and add to registry
        unique_sources = self._deduplicate_sources(all_sources)
        for source in unique_sources:
            self.registry.add_source(source)

        # Save updated registry
        self.registry.save_sources()

        return unique_sources

    def _deduplicate_sources(
        self, sources: List[DiscoveredSource]
    ) -> List[DiscoveredSource]:
        """Remove duplicate sources, keeping the highest confidence version"""
        source_map = {}

        for source in sources:
            existing = source_map.get(source.url)
            if not existing or source.confidence_score > existing.confidence_score:
                source_map[source.url] = source

        return list(source_map.values())

    def get_discovered_sources(self, **criteria) -> List[DiscoveredSource]:
        """Get discovered sources by criteria"""
        return self.registry.get_sources_by_criteria(**criteria)

    def validate_source(self, url: str) -> None:
        """Mark a source as validated"""
        self.registry.mark_source_validated(url)
        self.registry.save_sources()

    async def scheduled_discovery(
        self, seed_urls: List[str], interval_hours: int = 24
    ) -> None:
        """Run discovery on a schedule"""
        logger.info(f"Starting scheduled discovery every {interval_hours} hours")

        while True:
            try:
                sources = await self.discover_sources(seed_urls)
                logger.info(f"Scheduled discovery found {len(sources)} sources")
                await asyncio.sleep(interval_hours * 3600)  # Convert hours to seconds
            except Exception as e:
                logger.error(f"Error in scheduled discovery: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour before retrying


# Example usage and testing
async def demo_automated_discovery():
    """Demo function showing automated discovery in action"""
    config = {
        "bots": {
            "search_engine": {
                "google_api_key": "your-api-key-here",
                "google_search_engine_id": "your-search-engine-id",
                "target_regions": ["us", "uk", "canada"],
            }
        }
    }

    # Seed URLs for government and business sites
    seed_urls = [
        "https://www.usa.gov",
        "https://www.gov.uk",
        "https://europa.eu",
        "https://www.canada.ca",
    ]

    manager = AutomatedDiscoveryManager(config)

    print("🚀 Starting Automated Source Discovery Demo")
    print("=" * 50)

    # Run discovery
    sources = await manager.discover_sources(seed_urls)

    print(f"\n✅ Discovery completed! Found {len(sources)} sources")

    # Show results by category
    for source_type in [
        "business_registry",
        "procurement_portal",
        "business_directory",
    ]:
        filtered = manager.get_discovered_sources(
            source_type=source_type, min_confidence=0.5
        )
        if filtered:
            print(f"\n📋 {source_type.title()} Sources ({len(filtered)}):")
            for source in filtered[:3]:  # Show top 3
                print(f"  • {source.url}")
                print(
                    f"    Confidence: {source.confidence_score:.2f} | Region: {source.region}"
                )
                print(f"    Method: {source.discovery_method}")

    print(f"\n💾 All sources saved to registry: {manager.registry.storage_path}")


if __name__ == "__main__":
    asyncio.run(demo_automated_discovery())
