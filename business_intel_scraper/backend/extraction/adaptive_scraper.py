"""
Adaptive Business Scraper with Schema Detection Integration

This module implements the AdaptiveBusinessScraper that combines intelligent
crawling with automatic schema detection for efficient business intelligence extraction.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import json
from pathlib import Path
from urllib.parse import urljoin, urlparse

try:
    from playwright.async_api import async_playwright, Browser, Page

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

from ..discovery.scheduler import IntelligentCrawlScheduler, CrawlRequest, CrawlPriority
from ..discovery.classifier import AdaptiveLinkClassifier
from ..discovery.graph_analyzer import CrawlGraphAnalyzer
from .schema_detector import SchemaDetector, DetectedSchema

logger = logging.getLogger(__name__)


@dataclass
class ExtractionResult:
    """Result of data extraction from a page"""

    url: str
    schema_id: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    success: bool = False
    confidence: float = 0.0
    error: Optional[str] = None
    extracted_at: float = field(default_factory=time.time)
    response_time: float = 0.0
    extracted_links: List[str] = field(default_factory=list)


class AdaptiveBusinessScraper:
    """
    Adaptive scraper that combines intelligent discovery with schema-based extraction.

    Features:
    - ML-powered crawl scheduling and link classification
    - Automatic schema detection and evolution
    - Playwright-based dynamic content handling
    - Graph analysis for crawl optimization
    - Template-based extraction with confidence scoring
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

        # Initialize components
        self.scheduler = IntelligentCrawlScheduler(self.config.get("scheduler", {}))
        self.classifier = AdaptiveLinkClassifier(self.config.get("classifier", {}))
        self.graph_analyzer = CrawlGraphAnalyzer(self.config.get("graph_analyzer", {}))
        self.schema_detector = SchemaDetector(self.config.get("schema_detector", {}))

        # Browser management
        self.browser: Optional[Any] = None
        self.browser_context: Optional[Any] = None

        # State tracking
        self.active_extractions: Dict[str, ExtractionResult] = {}
        self.completed_extractions: List[ExtractionResult] = []
        self.known_schemas: Dict[str, DetectedSchema] = {}

        # Configuration
        self.max_concurrent_extractions = self.config.get(
            "max_concurrent_extractions", 5
        )
        self.page_timeout = self.config.get("page_timeout", 30000)
        self.retry_attempts = self.config.get("retry_attempts", 3)
        self.headless = self.config.get("headless", True)

        logger.info(
            f"AdaptiveBusinessScraper initialized (Playwright: {PLAYWRIGHT_AVAILABLE})"
        )

    async def start_browser(self) -> bool:
        """Start browser instance for scraping"""
        if not PLAYWRIGHT_AVAILABLE:
            logger.warning("Playwright not available, browser functionality disabled")
            return False

        try:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=self.headless, args=["--disable-dev-shm-usage", "--no-sandbox"]
            )
            self.browser_context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            )

            logger.info("Browser started successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            return False

    async def stop_browser(self) -> None:
        """Stop browser instance"""
        try:
            if self.browser_context:
                await self.browser_context.close()
            if self.browser:
                await self.browser.close()
            logger.info("Browser stopped")
        except Exception as e:
            logger.error(f"Error stopping browser: {e}")

    def add_seed_urls(
        self, urls: List[str], priority: CrawlPriority = CrawlPriority.NORMAL
    ) -> int:
        """Add seed URLs to start crawling"""
        added = 0
        for url in urls:
            request = CrawlRequest(
                url=url, spider_name="adaptive_scraper", priority=priority, depth=0
            )
            if self.scheduler.add_crawl_request(request):
                added += 1

        logger.info(f"Added {added} seed URLs to crawl queue")
        return added

    async def run_adaptive_crawl(
        self, max_pages: int = 100, time_limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """Run adaptive crawling session"""
        start_time = time.time()
        pages_processed = 0
        results = []

        logger.info(
            f"Starting adaptive crawl (max_pages: {max_pages}, time_limit: {time_limit}s)"
        )

        # Start browser if available
        if PLAYWRIGHT_AVAILABLE and not self.browser:
            await self.start_browser()

        try:
            while pages_processed < max_pages:
                # Check time limit
                if time_limit and (time.time() - start_time) > time_limit:
                    logger.info("Time limit reached, stopping crawl")
                    break

                # Get next crawl request
                request = self.scheduler.get_next_crawl_request()
                if not request:
                    # No more requests available
                    await asyncio.sleep(1)
                    continue

                # Process the request
                result = await self._process_crawl_request(request)
                results.append(result)
                pages_processed += 1

                # Update scheduler with results
                self.scheduler.complete_crawl_request(
                    request.url,
                    result.success,
                    result.response_time,
                    result.confidence,
                    result.extracted_links,
                )

                # Update graph analyzer
                self.graph_analyzer.add_crawl_result(
                    request.url,
                    request.parent_url,
                    result.extracted_links,
                    result.success,
                    result.confidence,
                    result.response_time,
                    {"schema_id": result.schema_id},
                )

                # Add discovered links to crawl queue
                if result.extracted_links:
                    await self._add_discovered_links(
                        result.extracted_links, request.url, request.depth + 1
                    )

                # Periodic optimization
                if pages_processed % 20 == 0:
                    await self._optimize_crawl_strategy()

                logger.info(f"Processed {pages_processed}/{max_pages} pages")

        except Exception as e:
            logger.error(f"Crawl session error: {e}")

        finally:
            if self.browser:
                await self.stop_browser()

        # Generate summary
        summary = self._generate_crawl_summary(results, time.time() - start_time)
        logger.info(f"Crawl completed: {summary}")

        return summary

    async def _process_crawl_request(self, request: CrawlRequest) -> ExtractionResult:
        """Process a single crawl request"""
        result = ExtractionResult(url=request.url)
        start_time = time.time()

        try:
            # Fetch page content
            if self.browser_context:
                html_content, links = await self._fetch_with_browser(request.url)
            else:
                html_content, links = await self._fetch_with_requests(request.url)

            result.extracted_links = links
            result.response_time = time.time() - start_time

            if not html_content:
                result.error = "Failed to fetch content"
                return result

            # Detect or match schema
            schema = await self._detect_or_match_schema(html_content, request.url)

            if schema:
                result.schema_id = schema.schema_id

                # Extract data using schema
                extracted_data = await self._extract_data_with_schema(
                    html_content, schema
                )
                result.data = extracted_data
                result.confidence = self._calculate_extraction_confidence(
                    extracted_data, schema
                )
                result.success = result.confidence > 0.3
            else:
                # Basic extraction without schema
                result.data = await self._basic_extraction(html_content, request.url)
                result.confidence = 0.2
                result.success = bool(result.data)

            logger.debug(
                f"Extraction result for {request.url}: success={result.success}, confidence={result.confidence:.2f}"
            )

        except Exception as e:
            result.error = str(e)
            result.response_time = time.time() - start_time
            logger.error(f"Failed to process {request.url}: {e}")

        return result

    async def _fetch_with_browser(self, url: str) -> Tuple[str, List[str]]:
        """Fetch content using Playwright browser"""
        if not self.browser_context:
            raise RuntimeError("Browser not initialized")

        page = await self.browser_context.new_page()
        try:
            # Navigate to page
            await page.goto(url, timeout=self.page_timeout)
            await page.wait_for_load_state("networkidle", timeout=10000)

            # Get HTML content
            html_content = await page.content()

            # Extract all links
            links = await page.evaluate(
                """
                () => {
                    const links = Array.from(document.querySelectorAll('a[href]'));
                    return links.map(link => {
                        const href = link.getAttribute('href');
                        return href ? new URL(href, window.location.href).href : null;
                    }).filter(Boolean);
                }
            """
            )

            return html_content, links

        finally:
            await page.close()

    async def _fetch_with_requests(self, url: str) -> Tuple[str, List[str]]:
        """Fallback: Fetch content using requests library"""
        try:
            import requests
            from bs4 import BeautifulSoup

            response = requests.get(
                url,
                timeout=30,
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; BusinessIntelligenceScraper/1.0)"
                },
            )
            response.raise_for_status()

            # Parse links
            soup = BeautifulSoup(response.content, "html.parser")
            links = []
            for a_tag in soup.find_all("a", href=True):
                link = urljoin(url, a_tag["href"])
                links.append(link)

            return response.text, links

        except Exception as e:
            logger.error(f"Requests fallback failed: {e}")
            return "", []

    async def _detect_or_match_schema(
        self, html_content: str, url: str
    ) -> Optional[DetectedSchema]:
        """Detect schema or match against existing schemas"""
        try:
            # Try to match against existing schemas first
            domain = urlparse(url).netloc
            matching_schemas = [
                schema
                for schema in self.known_schemas.values()
                if any(domain in sample_url for sample_url in schema.sample_urls)
            ]

            if matching_schemas:
                # Use best matching schema
                best_schema = max(matching_schemas, key=lambda s: s.confidence)
                logger.debug(f"Using existing schema {best_schema.schema_id} for {url}")
                return best_schema

            # Detect new schema
            schema = self.schema_detector.detect_schema(html_content, url)
            if schema:
                self.known_schemas[schema.schema_id] = schema
                logger.info(f"Detected new schema {schema.schema_id} for {url}")

                # Save schema for future use
                self.schema_detector.save_schema(schema)

                return schema

            return None

        except Exception as e:
            logger.error(f"Schema detection/matching failed for {url}: {e}")
            return None

    async def _extract_data_with_schema(
        self, html_content: str, schema: DetectedSchema
    ) -> Dict[str, Any]:
        """Extract data using detected schema"""
        extracted_data = {}

        try:
            if not schema.fields:
                return extracted_data

            # For simplified extraction without lxml, use regex patterns
            import re

            for field in schema.fields:
                if field.data_type.value == "email":
                    email_pattern = (
                        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
                    )
                    matches = re.findall(email_pattern, html_content)
                    if matches:
                        extracted_data[field.name] = (
                            matches[0] if not field.multiple else matches
                        )

                elif field.data_type.value == "phone":
                    phone_pattern = (
                        r"\b\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b"
                    )
                    matches = re.findall(phone_pattern, html_content)
                    if matches:
                        extracted_data[field.name] = (
                            matches[0] if not field.multiple else matches
                        )

                elif field.data_type.value == "url":
                    url_pattern = r'https?://[^\s<>"]{2,}'
                    matches = re.findall(url_pattern, html_content)
                    if matches:
                        extracted_data[field.name] = (
                            matches[0] if not field.multiple else matches[:5]
                        )

                elif field.data_type.value == "text":
                    # Simple text extraction based on field name
                    if field.name == "company_name":
                        title_match = re.search(
                            r"<title>([^<]+)</title>", html_content, re.I
                        )
                        if title_match:
                            extracted_data[field.name] = title_match.group(1).strip()

            return extracted_data

        except Exception as e:
            logger.error(f"Schema-based extraction failed: {e}")
            return extracted_data

    async def _basic_extraction(self, html_content: str, url: str) -> Dict[str, Any]:
        """Basic extraction without schema"""
        data = {}

        try:
            import re

            # Extract title
            title_match = re.search(r"<title>([^<]+)</title>", html_content, re.I)
            if title_match:
                data["title"] = title_match.group(1).strip()

            # Extract emails
            email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
            emails = re.findall(email_pattern, html_content)
            if emails:
                data["emails"] = list(set(emails))

            # Extract phone numbers
            phone_pattern = (
                r"\b\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b"
            )
            phones = re.findall(phone_pattern, html_content)
            if phones:
                data["phones"] = list(set(phones))

            # Extract URLs
            url_pattern = r'https?://[^\s<>"]{2,}'
            urls = re.findall(url_pattern, html_content)
            if urls:
                data["urls"] = list(set(urls))[:10]  # Limit to 10 URLs

            return data

        except Exception as e:
            logger.error(f"Basic extraction failed: {e}")
            return {}

    def _calculate_extraction_confidence(
        self, data: Dict[str, Any], schema: DetectedSchema
    ) -> float:
        """Calculate confidence score for extraction results"""
        if not schema.fields or not data:
            return 0.0

        # Count successfully extracted fields
        extracted_fields = sum(1 for field in schema.fields if field.name in data)
        critical_fields = sum(
            1
            for field in schema.fields
            if field.importance.value <= 2 and field.name in data
        )

        # Base score from extraction rate
        extraction_rate = extracted_fields / len(schema.fields)

        # Bonus for critical fields
        critical_bonus = critical_fields * 0.1

        # Schema confidence influence
        schema_influence = schema.confidence * 0.3

        confidence = (extraction_rate * 0.6) + critical_bonus + schema_influence
        return max(0.0, min(1.0, confidence))

    async def _add_discovered_links(
        self, links: List[str], parent_url: str, depth: int
    ) -> None:
        """Add discovered links to crawl queue with classification"""
        if not links:
            return

        # Classify links for priority
        link_data = [(link, "", parent_url) for link in links]
        classified_links = self.classifier.classify_links_batch(link_data)

        for link_info in classified_links:
            if link_info.priority.value <= 3:  # High to Medium priority
                request = CrawlRequest(
                    url=link_info.url,
                    spider_name="adaptive_scraper",
                    priority=self._link_priority_to_crawl_priority(link_info.priority),
                    depth=depth,
                    parent_url=parent_url,
                    metadata={
                        "link_category": link_info.category.value,
                        "link_confidence": link_info.confidence,
                    },
                )
                self.scheduler.add_crawl_request(request)

    def _link_priority_to_crawl_priority(self, link_priority: Any) -> CrawlPriority:
        """Convert link priority to crawl priority"""
        mapping = {
            1: CrawlPriority.CRITICAL,  # CRITICAL
            2: CrawlPriority.HIGH,  # HIGH
            3: CrawlPriority.NORMAL,  # MEDIUM
            4: CrawlPriority.LOW,  # LOW
            5: CrawlPriority.BACKGROUND,  # IGNORE -> BACKGROUND
        }
        return mapping.get(link_priority.value, CrawlPriority.NORMAL)

    async def _optimize_crawl_strategy(self) -> None:
        """Optimize crawl strategy based on current performance"""
        try:
            # Analyze crawl patterns
            analysis = self.graph_analyzer.analyze_crawl_patterns()

            if analysis.get("status") == "error":
                return

            # Get recommendations
            recommendations = analysis.get("recommendations", [])
            for rec in recommendations:
                logger.info(f"Crawl optimization: {rec}")

            # Get high-value targets
            high_value_targets = self.graph_analyzer.get_high_value_targets(10)
            for url, score in high_value_targets:
                # Add high-value targets with critical priority
                request = CrawlRequest(
                    url=url,
                    spider_name="adaptive_scraper",
                    priority=CrawlPriority.CRITICAL,
                    metadata={"optimization_score": score},
                )
                self.scheduler.add_crawl_request(request)

        except Exception as e:
            logger.error(f"Crawl optimization failed: {e}")

    def _generate_crawl_summary(
        self, results: List[ExtractionResult], duration: float
    ) -> Dict[str, Any]:
        """Generate comprehensive crawl session summary"""
        total_results = len(results)
        successful_results = sum(1 for r in results if r.success)

        # Schema usage stats
        schema_usage = {}
        for result in results:
            if result.schema_id:
                schema_usage[result.schema_id] = (
                    schema_usage.get(result.schema_id, 0) + 1
                )

        # Data extraction stats
        total_data_points = sum(len(r.data) for r in results)
        avg_confidence = (
            sum(r.confidence for r in results) / total_results
            if total_results > 0
            else 0.0
        )
        avg_response_time = (
            sum(r.response_time for r in results) / total_results
            if total_results > 0
            else 0.0
        )

        return {
            "duration": duration,
            "total_pages": total_results,
            "successful_extractions": successful_results,
            "success_rate": (
                successful_results / total_results if total_results > 0 else 0.0
            ),
            "avg_confidence": avg_confidence,
            "avg_response_time": avg_response_time,
            "total_data_points": total_data_points,
            "schemas_used": len(schema_usage),
            "schema_usage": schema_usage,
            "scheduler_stats": self.scheduler.get_scheduler_stats(),
            "classifier_stats": self.classifier.get_classifier_stats(),
            "graph_stats": self.graph_analyzer.get_analyzer_stats(),
        }

    def get_scraper_stats(self) -> Dict[str, Any]:
        """Get comprehensive scraper statistics"""
        return {
            "total_extractions": len(self.completed_extractions),
            "active_extractions": len(self.active_extractions),
            "known_schemas": len(self.known_schemas),
            "browser_available": PLAYWRIGHT_AVAILABLE and self.browser is not None,
            "scheduler": self.scheduler.get_scheduler_stats(),
            "classifier": self.classifier.get_classifier_stats(),
            "graph_analyzer": self.graph_analyzer.get_analyzer_stats(),
            "schema_detector": self.schema_detector.get_detector_stats(),
        }

    async def export_results(self, filepath: str, format: str = "json") -> bool:
        """Export extraction results"""
        try:
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)

            results_data = [
                {
                    "url": result.url,
                    "schema_id": result.schema_id,
                    "data": result.data,
                    "success": result.success,
                    "confidence": result.confidence,
                    "extracted_at": result.extracted_at,
                    "response_time": result.response_time,
                    "extracted_links_count": len(result.extracted_links),
                }
                for result in self.completed_extractions
            ]

            if format.lower() == "json":
                with open(path, "w") as f:
                    json.dump(results_data, f, indent=2)
            elif format.lower() == "csv":
                import pandas as pd

                df = pd.json_normalize(results_data)
                df.to_csv(path, index=False)

            logger.info(f"Exported {len(results_data)} results to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False
