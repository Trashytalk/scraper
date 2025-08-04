"""
Real Web Scraping Engine for Business Intelligence Scraper
Provides actual web scraping functionality using multiple backends
"""

import asyncio
import json
import logging
import re
import sqlite3
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScrapingEngine:
    """Main scraping engine with multiple backend support"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )

    async def scrape_url(
        self, url: str, scraper_type: str = "basic", config: Dict = None
    ) -> Dict[str, Any]:
        """
        Main scraping method that dispatches to appropriate scraper
        """
        config = config or {}

        try:
            if scraper_type == "basic":
                return await self._basic_scraper(url, config)
            elif scraper_type == "e_commerce":
                return await self._ecommerce_scraper(url, config)
            elif scraper_type == "news":
                return await self._news_scraper(url, config)
            elif scraper_type == "social_media":
                return await self._social_media_scraper(url, config)
            elif scraper_type == "api":
                return await self._api_scraper(url, config)
            elif scraper_type == "intelligent":
                return await self._intelligent_scraper(url, config)
            else:
                return await self._basic_scraper(url, config)

        except Exception as e:
            logger.error(f"Scraping failed for {url}: {str(e)}")
            return {
                "url": url,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def intelligent_crawl(
        self, seed_url: str, scraper_type: str = "basic", config: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Intelligent crawling that discovers and follows links from seed URL
        Enhanced with full HTML extraction, domain crawling, and comprehensive status tracking
        """
        config = config or {}

        # Enhanced crawling configuration
        max_pages = config.get("max_pages", 50)
        print(
            f"DEBUG: max_pages set to {max_pages} from config: {config.get('max_pages', 'NOT SET')}"
        )
        max_depth = config.get("max_depth", 3)
        follow_internal_links = config.get("follow_internal_links", True)
        follow_external_links = config.get("follow_external_links", False)
        include_patterns = config.get("include_patterns", "")
        exclude_patterns = config.get("exclude_patterns", "")

        # NEW: Enhanced extraction options
        extract_full_html = config.get("extract_full_html", False)
        crawl_entire_domain = config.get("crawl_entire_domain", False)
        include_images = config.get("include_images", False)
        save_to_database = config.get("save_to_database", True)

        # Rate limiting configuration
        rate_limit = config.get("rate_limit", {})
        requests_per_second = rate_limit.get("requests_per_second", 1.0)
        max_concurrent_workers = config.get("max_concurrent_workers", 5)

        # Enhanced crawl results with comprehensive tracking
        start_time = time.time()
        crawl_results = {
            "seed_url": seed_url,
            "job_type": "intelligent_crawling",
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "start_time": start_time,
            "config": {
                "max_pages": max_pages,
                "max_depth": max_depth,
                "extract_full_html": extract_full_html,
                "crawl_entire_domain": crawl_entire_domain,
                "include_images": include_images,
                "follow_internal_links": follow_internal_links,
                "follow_external_links": follow_external_links,
            },
            "summary": {
                "pages_processed": 0,
                "urls_discovered": 0,
                "urls_queued": 0,
                "data_extracted": 0,
                "total_crawl_time": 0,
                "average_page_time": 0,
                "duplicate_pages_skipped": 0,
                "errors_encountered": 0,
                "images_extracted": 0,
                "domains_crawled": set(),
            },
            "crawled_data": [],
            "discovered_urls": [],
            "errors": [],
            "duplicate_urls": [],
            "crawl_status": "in_progress",
        }

        try:
            # Initialize crawling state with enhanced tracking
            url_queue = [{"url": seed_url, "depth": 0}]
            visited_urls = set()
            discovered_urls = set()
            page_times = []

            import re as regex
            from urllib.parse import urljoin, urlparse

            seed_domain = urlparse(seed_url).netloc
            crawl_results["summary"]["domains_crawled"].add(seed_domain)

            # Enhanced domain crawling logic
            if crawl_entire_domain:
                max_pages = (
                    max_pages if max_pages > 0 else 1000
                )  # Increase limit for domain crawls
                max_depth = max(
                    max_depth, 5
                )  # Ensure sufficient depth for domain exploration

            # Database connection for persistence
            db_conn = None
            if save_to_database:
                try:
                    db_conn = sqlite3.connect("data.db")
                    cursor = db_conn.cursor()
                    # Create tables if they don't exist
                    cursor.execute(
                        """
                        CREATE TABLE IF NOT EXISTS crawl_cache (
                            url TEXT PRIMARY KEY,
                            content TEXT,
                            metadata TEXT,
                            crawled_at TIMESTAMP,
                            domain TEXT
                        )
                    """
                    )
                    db_conn.commit()
                except Exception as e:
                    logger.warning(
                        f"Database connection failed, proceeding without persistence: {e}"
                    )
                    db_conn = None

            while url_queue and len(visited_urls) < max_pages:
                current_item = url_queue.pop(0)
                current_url = current_item["url"]
                current_depth = current_item["depth"]

                # Skip if already visited or max depth reached
                if current_url in visited_urls or current_depth > max_depth:
                    if current_url in visited_urls:
                        crawl_results["duplicate_urls"].append(current_url)
                        crawl_results["summary"]["duplicate_pages_skipped"] += 1
                    continue

                visited_urls.add(current_url)
                page_start_time = time.time()

                # Check if page was previously crawled (if database is available)
                cached_data = None
                if db_conn:
                    try:
                        cursor = db_conn.cursor()
                        cursor.execute(
                            "SELECT content, metadata, crawled_at FROM crawl_cache WHERE url = ?",
                            (current_url,),
                        )
                        cached_result = cursor.fetchone()
                        if cached_result:
                            cached_data = {
                                "url": current_url,
                                "cached": True,
                                "cached_at": cached_result[2],
                                "data": (
                                    json.loads(cached_result[1])
                                    if cached_result[1]
                                    else {}
                                ),
                            }
                            logger.info(f"Using cached data for {current_url}")
                    except Exception as e:
                        logger.warning(f"Cache lookup failed for {current_url}: {e}")

                try:
                    # Rate limiting
                    await asyncio.sleep(1.0 / requests_per_second)

                    # Scrape current page (or use cached data)
                    if cached_data:
                        page_data = cached_data["data"]
                        page_data["cached"] = True
                        page_data["cached_at"] = cached_data["cached_at"]
                    else:
                        # Enhanced scraping with full HTML option
                        enhanced_config = {**config}
                        if extract_full_html:
                            enhanced_config["extract_full_html"] = True
                        if include_images:
                            enhanced_config["include_all_images"] = True
                            enhanced_config["include_images"] = True

                        page_data = await self.scrape_url(
                            current_url, scraper_type, enhanced_config
                        )

                    if page_data.get("status") == "success":
                        # Track page processing time
                        page_end_time = time.time()
                        page_time = page_end_time - page_start_time
                        page_times.append(page_time)

                        # Add crawling metadata
                        page_data["crawl_metadata"] = {
                            "depth": current_depth,
                            "processing_time": page_time,
                            "discovery_order": len(crawl_results["crawled_data"]) + 1,
                            "domain": urlparse(current_url).netloc,
                        }

                        # Save to database if enabled
                        if db_conn and not cached_data:
                            try:
                                cursor = db_conn.cursor()
                                cursor.execute(
                                    "INSERT OR REPLACE INTO crawl_cache (url, content, metadata, crawled_at, domain) VALUES (?, ?, ?, ?, ?)",
                                    (
                                        current_url,
                                        page_data.get("raw_html", ""),
                                        json.dumps(page_data),
                                        datetime.now().isoformat(),
                                        urlparse(current_url).netloc,
                                    ),
                                )
                                db_conn.commit()
                            except Exception as e:
                                logger.warning(
                                    f"Failed to cache data for {current_url}: {e}"
                                )

                        crawl_results["crawled_data"].append(page_data)
                        crawl_results["summary"]["pages_processed"] += 1
                        crawl_results["summary"]["data_extracted"] += 1

                        # Count images if extracted
                        if include_images and "images" in page_data:
                            image_count = len(page_data.get("images", []))
                            crawl_results["summary"]["images_extracted"] += image_count
                            print(
                                f"DEBUG: Found {image_count} images on page {current_url}, total now: {crawl_results['summary']['images_extracted']}"
                            )
                        elif include_images:
                            print(
                                f"DEBUG: include_images=True but no 'images' key in page_data for {current_url}"
                            )
                            print(
                                f"DEBUG: page_data keys: {list(page_data.keys()) if page_data else 'No page_data'}"
                            )
                        else:
                            print(
                                f"DEBUG: include_images={include_images} for {current_url}"
                            )

                        # Track domain coverage
                        page_domain = urlparse(current_url).netloc
                        crawl_results["summary"]["domains_crawled"].add(page_domain)

                        # Extract links for further crawling
                        if current_depth < max_depth:
                            links = page_data.get("links", [])

                            for link in links:
                                if isinstance(link, dict):
                                    link_url = link.get("url", "")
                                else:
                                    link_url = str(link)

                                if not link_url or link_url in visited_urls:
                                    continue

                                # Make URL absolute
                                absolute_url = urljoin(current_url, link_url)
                                parsed_url = urlparse(absolute_url)

                                # Enhanced domain filtering for entire domain crawling
                                is_internal = parsed_url.netloc == seed_domain
                                is_subdomain = parsed_url.netloc.endswith(
                                    "." + seed_domain
                                )

                                # Allow subdomains if crawling entire domain
                                domain_match = is_internal or (
                                    crawl_entire_domain and is_subdomain
                                )

                                if not (
                                    (domain_match and follow_internal_links)
                                    or (not domain_match and follow_external_links)
                                ):
                                    continue

                                # Apply include/exclude patterns
                                if include_patterns and not regex.search(
                                    include_patterns, absolute_url
                                ):
                                    continue
                                if exclude_patterns and regex.search(
                                    exclude_patterns, absolute_url
                                ):
                                    continue

                                # Add to queue if not already discovered
                                if absolute_url not in discovered_urls:
                                    discovered_urls.add(absolute_url)
                                    url_queue.append(
                                        {
                                            "url": absolute_url,
                                            "depth": current_depth + 1,
                                        }
                                    )
                                    crawl_results["discovered_urls"].append(
                                        absolute_url
                                    )
                                    crawl_results["summary"]["urls_discovered"] += 1
                                    crawl_results["summary"]["urls_queued"] += 1

                except Exception as e:
                    logger.error(f"Error crawling {current_url}: {str(e)}")
                    crawl_results["errors"].append(
                        {
                            "url": current_url,
                            "error": str(e),
                            "timestamp": datetime.now().isoformat(),
                            "depth": current_depth,
                        }
                    )
                    crawl_results["summary"]["errors_encountered"] += 1

            # Calculate final statistics
            end_time = time.time()
            total_time = end_time - start_time
            crawl_results["summary"]["total_crawl_time"] = round(total_time, 2)
            crawl_results["summary"]["average_page_time"] = round(
                sum(page_times) / len(page_times) if page_times else 0, 2
            )
            crawl_results["summary"]["domains_crawled"] = list(
                crawl_results["summary"]["domains_crawled"]
            )
            crawl_results["crawl_status"] = "completed"
            crawl_results["end_time"] = end_time

            # Close database connection
            if db_conn:
                db_conn.close()

            logger.info(
                f"Crawling completed: {crawl_results['summary']['pages_processed']} pages processed, "
                f"{crawl_results['summary']['urls_discovered']} URLs discovered, "
                f"Total time: {total_time:.2f}s, "
                f"Domains: {len(crawl_results['summary']['domains_crawled'])}"
            )

            return crawl_results

        except Exception as e:
            logger.error(f"Intelligent crawling failed for {seed_url}: {str(e)}")
            crawl_results["status"] = "error"
            crawl_results["error"] = str(e)
            return crawl_results

    async def _intelligent_scraper(self, url: str, config: Dict) -> Dict[str, Any]:
        """
        Intelligent scraper that automatically detects content type and uses appropriate extraction
        """
        try:
            # Start with basic scraping
            basic_result = await self._basic_scraper(url, config)

            if basic_result.get("status") != "success":
                return basic_result

            # Analyze content to determine best extraction strategy
            soup = BeautifulSoup(basic_result.get("raw_html", ""), "html.parser")

            # Check for e-commerce indicators
            ecommerce_indicators = [
                ".price",
                ".add-to-cart",
                ".product",
                ".cart",
                ".buy",
                ".shop",
            ]
            if any(soup.select(indicator) for indicator in ecommerce_indicators):
                logger.info(
                    f"Detected e-commerce content for {url}, using e-commerce scraper"
                )
                return await self._ecommerce_scraper(url, config)

            # Check for news indicators
            news_indicators = [
                "article",
                ".article",
                ".news",
                "[class*='headline']",
                "[class*='story']",
                "time[datetime]",
                ".byline",
                ".author",
            ]
            if any(soup.select(indicator) for indicator in news_indicators):
                logger.info(f"Detected news content for {url}, using news scraper")
                return await self._news_scraper(url, config)

            # Check for social media indicators
            social_indicators = [
                ".post",
                ".tweet",
                ".feed",
                ".timeline",
                ".comment",
                ".like",
                ".share",
            ]
            if any(soup.select(indicator) for indicator in social_indicators):
                logger.info(
                    f"Detected social media content for {url}, using social media scraper"
                )
                return await self._social_media_scraper(url, config)

            # Default to enhanced basic scraping with auto-detection
            logger.info(f"Using intelligent basic scraping for {url}")

            # Enhance basic result with intelligent extraction
            enhanced_data = {
                **basic_result,
                "content_type": "intelligent_detection",
                "auto_extracted": {
                    "key_information": self._extract_key_information(soup),
                    "structured_data": self._extract_structured_data(soup),
                    "contact_info": self._extract_contact_info(soup),
                    "social_links": self._extract_social_links(soup),
                },
            }

            return enhanced_data

        except Exception as e:
            logger.error(f"Intelligent scraping failed for {url}: {str(e)}")
            return {
                "url": url,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _extract_key_information(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract key information using heuristics"""
        key_info = {}

        # Extract important headings
        headings = []
        for h in soup.find_all(["h1", "h2", "h3"]):
            text = h.get_text().strip()
            if text and len(text) > 5:
                headings.append(text)
        key_info["headings"] = headings[:10]

        # Extract contact information
        text_content = soup.get_text()
        import re

        # Email addresses
        emails = re.findall(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text_content
        )
        key_info["emails"] = list(set(emails))[:5]

        # Phone numbers
        phones = re.findall(r"[\+]?[1-9]?[\d\s\-\(\)]{10,20}", text_content)
        key_info["phones"] = list(set(phones))[:5]

        return key_info

    def _extract_structured_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract structured data like JSON-LD, microdata"""
        structured = {}

        # JSON-LD
        scripts = soup.find_all("script", type="application/ld+json")
        json_ld = []
        for script in scripts:
            try:
                data = json.loads(script.string)
                json_ld.append(data)
            except (json.JSONDecodeError, AttributeError):
                continue
        structured["json_ld"] = json_ld

        # Microdata
        microdata = []
        for item in soup.find_all(attrs={"itemscope": True}):
            item_data = {"type": item.get("itemtype", "")}
            props = {}
            for prop in item.find_all(attrs={"itemprop": True}):
                props[prop.get("itemprop")] = prop.get_text().strip()
            item_data["properties"] = props
            microdata.append(item_data)
        structured["microdata"] = microdata

        return structured

    def _extract_contact_info(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extract contact information"""
        contact = {"addresses": [], "phone_numbers": [], "email_addresses": []}

        # Look for address patterns
        address_keywords = ["address", "location", "contact", "office"]
        for keyword in address_keywords:
            elements = soup.find_all(text=re.compile(keyword, re.I))
            for element in elements:
                parent = element.parent
                if parent:
                    text = parent.get_text().strip()
                    if len(text) > 20 and len(text) < 200:
                        contact["addresses"].append(text)

        return contact

    def _extract_social_links(self, soup: BeautifulSoup) -> List[str]:
        """Extract social media links"""
        social_domains = [
            "facebook.com",
            "twitter.com",
            "instagram.com",
            "linkedin.com",
            "youtube.com",
            "tiktok.com",
            "pinterest.com",
            "snapchat.com",
        ]

        social_links = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if any(domain in href for domain in social_domains):
                social_links.append(href)

        return list(set(social_links))

    async def _basic_scraper(self, url: str, config: Dict) -> Dict[str, Any]:
        """Enhanced basic web page scraper with full HTML and comprehensive image extraction"""
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self._fetch_url, url)

            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.reason}")

            soup = BeautifulSoup(response.content, "html.parser")

            # Extract basic data
            data = {
                "url": url,
                "title": self._extract_title(soup),
                "meta_description": self._extract_meta_description(soup),
                "headings": self._extract_headings(soup),
                "links": self._extract_links(soup, url),
                "text_content": self._extract_text_content(soup),
                "images": self._extract_images(
                    soup, url, config.get("include_all_images", False)
                ),
                "word_count": len(soup.get_text().split()),
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "response_time": response.elapsed.total_seconds(),
            }

            # NEW: Add full HTML if requested
            if config.get("extract_full_html", False):
                data["raw_html"] = str(soup)
                data["html_size_bytes"] = len(response.content)
                data["content_encoding"] = response.encoding

            # NEW: Enhanced metadata extraction
            data["page_metadata"] = {
                "content_type": response.headers.get("content-type", ""),
                "last_modified": response.headers.get("last-modified", ""),
                "content_length": response.headers.get("content-length", ""),
                "server": response.headers.get("server", ""),
                "status_code": response.status_code,
                "final_url": response.url,  # In case of redirects
                "redirect_count": len(response.history),
            }

            # Add custom selectors if specified
            if config.get("custom_selectors"):
                data["custom_data"] = self._extract_custom_data(
                    soup, config["custom_selectors"]
                )

            return data

        except Exception as e:
            raise Exception(f"Basic scraping failed: {str(e)}")

    async def _ecommerce_scraper(self, url: str, config: Dict) -> Dict[str, Any]:
        """E-commerce specific scraper for product information"""
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self._fetch_url, url)
            soup = BeautifulSoup(response.content, "html.parser")

            data = {
                "url": url,
                "product_name": self._extract_product_name(soup),
                "price": self._extract_price(soup),
                "availability": self._extract_availability(soup),
                "rating": self._extract_rating(soup),
                "description": self._extract_product_description(soup),
                "images": self._extract_product_images(soup, url),
                "specifications": self._extract_specifications(soup),
                "reviews_count": self._extract_reviews_count(soup),
                "category": self._extract_category(soup),
                "brand": self._extract_brand(soup),
                "status": "success",
                "timestamp": datetime.now().isoformat(),
            }

            return data

        except Exception as e:
            raise Exception(f"E-commerce scraping failed: {str(e)}")

    async def _news_scraper(self, url: str, config: Dict) -> Dict[str, Any]:
        """News article scraper"""
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self._fetch_url, url)
            soup = BeautifulSoup(response.content, "html.parser")

            data = {
                "url": url,
                "headline": self._extract_headline(soup),
                "author": self._extract_author(soup),
                "publish_date": self._extract_publish_date(soup),
                "article_content": self._extract_article_content(soup),
                "tags": self._extract_tags(soup),
                "category": self._extract_news_category(soup),
                "word_count": len(soup.get_text().split()),
                "reading_time": self._estimate_reading_time(soup.get_text()),
                "status": "success",
                "timestamp": datetime.now().isoformat(),
            }

            return data

        except Exception as e:
            raise Exception(f"News scraping failed: {str(e)}")

    async def _social_media_scraper(self, url: str, config: Dict) -> Dict[str, Any]:
        """Social media content scraper (limited by platform APIs)"""
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self._fetch_url, url)
            soup = BeautifulSoup(response.content, "html.parser")

            # Extract open graph data common to social platforms
            data = {
                "url": url,
                "title": self._extract_og_title(soup),
                "description": self._extract_og_description(soup),
                "image": self._extract_og_image(soup),
                "site_name": self._extract_og_site_name(soup),
                "type": self._extract_og_type(soup),
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "note": "Social media scraping is limited due to platform restrictions",
            }

            return data

        except Exception as e:
            raise Exception(f"Social media scraping failed: {str(e)}")

    async def _api_scraper(self, url: str, config: Dict) -> Dict[str, Any]:
        """API endpoint scraper for JSON/XML data"""
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self._fetch_url, url)

            content_type = response.headers.get("content-type", "").lower()

            if "json" in content_type:
                data = response.json()
                return {
                    "url": url,
                    "content_type": "json",
                    "data": data,
                    "record_count": len(data) if isinstance(data, list) else 1,
                    "status": "success",
                    "timestamp": datetime.now().isoformat(),
                }
            elif "xml" in content_type:
                return {
                    "url": url,
                    "content_type": "xml",
                    "data": response.text,
                    "status": "success",
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                return {
                    "url": url,
                    "content_type": content_type,
                    "data": response.text[:1000],  # Truncate large responses
                    "status": "success",
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            raise Exception(f"API scraping failed: {str(e)}")

    def _fetch_url(self, url: str) -> requests.Response:
        """Fetch URL with retry logic"""
        for attempt in range(3):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                if attempt == 2:  # Last attempt
                    raise e
                time.sleep(1)  # Wait before retry

    # Extraction helper methods
    def _extract_title(self, soup: BeautifulSoup) -> str:
        title_tag = soup.find("title")
        return title_tag.get_text().strip() if title_tag else ""

    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        meta_desc = soup.find("meta", attrs={"name": "description"})
        return meta_desc.get("content", "") if meta_desc else ""

    def _extract_headings(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        headings = {}
        for i in range(1, 7):
            h_tags = soup.find_all(f"h{i}")
            headings[f"h{i}"] = [h.get_text().strip() for h in h_tags]
        return headings

    def _extract_links(
        self, soup: BeautifulSoup, base_url: str
    ) -> List[Dict[str, str]]:
        links = []
        for a_tag in soup.find_all("a", href=True):
            href = a_tag.get("href")
            if href:
                absolute_url = urljoin(base_url, href)
                links.append({"text": a_tag.get_text().strip(), "url": absolute_url})
        return links[:50]  # Limit to first 50 links

    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        text = soup.get_text()
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = " ".join(chunk for chunk in chunks if chunk)

        return text[:2000]  # Truncate to 2000 characters

    def _extract_images(
        self, soup: BeautifulSoup, base_url: str, include_all_images: bool = False
    ) -> List[Dict[str, str]]:
        """Enhanced image extraction with optional comprehensive image gathering"""
        images = []
        image_selectors = ["img[src]"]

        # If including all images, add more comprehensive selectors
        if include_all_images:
            image_selectors.extend(
                [
                    "img[data-src]",  # Lazy-loaded images
                    "img[data-lazy]",
                    "img[data-original]",
                    "[style*='background-image']",  # CSS background images
                    "picture source[srcset]",  # Responsive images
                    "video[poster]",  # Video thumbnails
                ]
            )

        # Extract regular img tags
        for selector in (
            image_selectors[:3] if not include_all_images else image_selectors[:6]
        ):
            for img_tag in soup.select(selector):
                src_attrs = ["src", "data-src", "data-lazy", "data-original"]
                src = None

                for attr in src_attrs:
                    src = img_tag.get(attr)
                    if src:
                        break

                if src:
                    absolute_url = urljoin(base_url, src)
                    image_data = {
                        "src": absolute_url,
                        "alt": img_tag.get("alt", ""),
                        "title": img_tag.get("title", ""),
                        "type": "img_tag",
                    }

                    # Add additional metadata if including all images
                    if include_all_images:
                        image_data.update(
                            {
                                "width": img_tag.get("width", ""),
                                "height": img_tag.get("height", ""),
                                "class": " ".join(img_tag.get("class", [])),
                                "loading": img_tag.get("loading", ""),
                                "srcset": img_tag.get("srcset", ""),
                            }
                        )

                    images.append(image_data)

        # Extract background images if including all images
        if include_all_images:
            import re

            for element in soup.select("[style*='background-image']"):
                style = element.get("style", "")
                bg_images = re.findall(
                    r'background-image:\s*url\(["\']?([^"\']+)["\']?\)', style
                )
                for bg_img in bg_images:
                    absolute_url = urljoin(base_url, bg_img)
                    images.append(
                        {
                            "src": absolute_url,
                            "alt": element.get("alt", ""),
                            "title": element.get("title", ""),
                            "type": "background_image",
                            "element_tag": element.name,
                            "element_class": " ".join(element.get("class", [])),
                        }
                    )

        # Limit images based on mode
        limit = 100 if include_all_images else 20
        return images[:limit]

    def _extract_custom_data(
        self, soup: BeautifulSoup, selectors: Dict[str, str]
    ) -> Dict[str, Any]:
        custom_data = {}
        for key, selector in selectors.items():
            try:
                elements = soup.select(selector)
                if elements:
                    if len(elements) == 1:
                        custom_data[key] = elements[0].get_text().strip()
                    else:
                        custom_data[key] = [el.get_text().strip() for el in elements]
                else:
                    custom_data[key] = None
            except Exception as e:
                custom_data[key] = f"Error: {str(e)}"
        return custom_data

    # E-commerce specific extractors
    def _extract_product_name(self, soup: BeautifulSoup) -> str:
        selectors = [
            'h1[class*="product"]',
            'h1[class*="title"]',
            ".product-name",
            ".product-title",
            "h1",
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()
        return ""

    def _extract_price(self, soup: BeautifulSoup) -> str:
        selectors = [
            '[class*="price"]',
            '[class*="cost"]',
            '[data-testid*="price"]',
            'span[class*="currency"]',
        ]

        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text().strip()
                # Look for currency patterns
                if re.search(r"[\$£€¥₹]\s*\d+|(\d+[\.,]\d{2})", text):
                    return text
        return ""

    def _extract_availability(self, soup: BeautifulSoup) -> str:
        selectors = [
            '[class*="stock"]',
            '[class*="availability"]',
            '[class*="inventory"]',
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()
        return ""

    def _extract_rating(self, soup: BeautifulSoup) -> str:
        selectors = ['[class*="rating"]', '[class*="star"]', '[class*="review-score"]']

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text().strip()
                # Look for rating patterns
                if re.search(
                    r"\d+\.?\d*\s*(?:out of|/|\|)\s*\d+|\d+\.?\d*\s*stars?",
                    text,
                    re.IGNORECASE,
                ):
                    return text
        return ""

    # News specific extractors
    def _extract_headline(self, soup: BeautifulSoup) -> str:
        selectors = [
            'h1[class*="headline"]',
            'h1[class*="title"]',
            ".article-title",
            ".entry-title",
            "h1",
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()
        return ""

    def _extract_author(self, soup: BeautifulSoup) -> str:
        selectors = ['[class*="author"]', '[class*="byline"]', '[rel="author"]']

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()
        return ""

    def _extract_publish_date(self, soup: BeautifulSoup) -> str:
        selectors = ["time[datetime]", '[class*="date"]', '[class*="publish"]']

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                # Try to get datetime attribute first
                datetime_attr = element.get("datetime")
                if datetime_attr:
                    return datetime_attr
                return element.get_text().strip()
        return ""

    def _extract_article_content(self, soup: BeautifulSoup) -> str:
        selectors = [
            ".article-content",
            ".entry-content",
            ".post-content",
            "article",
            ".content",
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                # Remove unwanted elements
                for unwanted in element.select(
                    "script, style, .advertisement, .social-share"
                ):
                    unwanted.decompose()
                return element.get_text().strip()[:3000]  # Limit content length
        return ""

    # Open Graph extractors
    def _extract_og_title(self, soup: BeautifulSoup) -> str:
        og_title = soup.find("meta", property="og:title")
        return og_title.get("content", "") if og_title else self._extract_title(soup)

    def _extract_og_description(self, soup: BeautifulSoup) -> str:
        og_desc = soup.find("meta", property="og:description")
        return (
            og_desc.get("content", "")
            if og_desc
            else self._extract_meta_description(soup)
        )

    def _extract_og_image(self, soup: BeautifulSoup) -> str:
        og_image = soup.find("meta", property="og:image")
        return og_image.get("content", "") if og_image else ""

    def _extract_og_site_name(self, soup: BeautifulSoup) -> str:
        og_site = soup.find("meta", property="og:site_name")
        return og_site.get("content", "") if og_site else ""

    def _extract_og_type(self, soup: BeautifulSoup) -> str:
        og_type = soup.find("meta", property="og:type")
        return og_type.get("content", "") if og_type else ""

    # Utility methods
    def _extract_tags(self, soup: BeautifulSoup) -> List[str]:
        tags = []
        # Look for meta keywords
        meta_keywords = soup.find("meta", attrs={"name": "keywords"})
        if meta_keywords:
            tags.extend(
                [tag.strip() for tag in meta_keywords.get("content", "").split(",")]
            )

        # Look for tag elements
        for tag_element in soup.select(".tag, .tags, .category, .categories"):
            tags.append(tag_element.get_text().strip())

        return list(set(tags))  # Remove duplicates

    def _extract_news_category(self, soup: BeautifulSoup) -> str:
        selectors = [".category", ".section", '[class*="category"]']

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()
        return ""

    def _estimate_reading_time(self, text: str) -> str:
        words = len(text.split())
        minutes = max(1, words // 200)  # Average reading speed: 200 WPM
        return f"{minutes} min read"

    def _extract_product_description(self, soup: BeautifulSoup) -> str:
        selectors = [
            ".product-description",
            ".description",
            '[class*="product"][class*="detail"]',
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()[:1000]
        return ""

    def _extract_product_images(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        images = []
        selectors = [
            ".product-image img",
            ".gallery img",
            '[class*="product"][class*="image"] img',
        ]

        for selector in selectors:
            for img in soup.select(selector):
                src = img.get("src")
                if src:
                    images.append(urljoin(base_url, src))

        return list(set(images))[:10]  # Remove duplicates, limit to 10

    def _extract_specifications(self, soup: BeautifulSoup) -> Dict[str, str]:
        specs = {}

        # Look for specification tables
        for table in soup.select(".specifications table, .specs table, .details table"):
            for row in table.select("tr"):
                cells = row.select("td, th")
                if len(cells) >= 2:
                    key = cells[0].get_text().strip()
                    value = cells[1].get_text().strip()
                    if key and value:
                        specs[key] = value

        return specs

    def _extract_reviews_count(self, soup: BeautifulSoup) -> str:
        selectors = [
            '[class*="review"][class*="count"]',
            '[class*="rating"][class*="count"]',
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text().strip()
                # Look for number patterns
                match = re.search(r"\d+", text)
                if match:
                    return match.group()
        return ""

    def _extract_category(self, soup: BeautifulSoup) -> str:
        selectors = [".breadcrumb a", ".category", '[class*="breadcrumb"]']

        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                return " > ".join([el.get_text().strip() for el in elements])
        return ""

    def _extract_brand(self, soup: BeautifulSoup) -> str:
        selectors = ['[class*="brand"]', '[class*="manufacturer"]', ".product-brand"]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()
        return ""


# Global scraping engine instance
scraping_engine = ScrapingEngine()


async def execute_scraping_job(
    job_id: int, job_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute a scraping job and store results in database
    """
    DATABASE_PATH = "/home/homebrew/scraper/data/scraper.db"

    try:
        url = job_config.get("url")
        job_type = job_config.get("type", "single_page")
        scraper_type = job_config.get("scraper_type", "basic")

        # Extract nested config if it exists, otherwise use the job_config directly
        if "config" in job_config and isinstance(job_config["config"], dict):
            config = job_config["config"]
        else:
            config = {}

        # Merge top-level crawling parameters into config for intelligent crawling
        if job_type == "intelligent_crawling":
            crawling_params = [
                "max_depth",
                "max_pages",
                "follow_internal_links",
                "follow_external_links",
                "include_patterns",
                "exclude_patterns",
                "rate_limit",
                "max_concurrent_workers",
            ]

            for param in crawling_params:
                if param in job_config:
                    config[param] = job_config[param]

        if not url:
            raise ValueError("No URL provided for scraping")

        # Handle different job types
        if job_type == "intelligent_crawling":
            result = await scraping_engine.intelligent_crawl(url, scraper_type, config)
        else:  # single_page or legacy types
            result = await scraping_engine.scrape_url(url, scraper_type, config)

        # Store results in database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Store the scraped data
        cursor.execute(
            """
            INSERT INTO job_results (job_id, data)
            VALUES (?, ?)
        """,
            (job_id, json.dumps(result)),
        )

        # Calculate results count and summary data
        if job_type == "intelligent_crawling":
            summary = result.get("summary", {})
            results_count = summary.get("data_extracted", 0)

            # Store additional summary data in job metadata
            cursor.execute(
                """
                UPDATE jobs 
                SET status = 'completed', 
                    completed_at = CURRENT_TIMESTAMP,
                    results_count = ?,
                    config = json_set(config, '$.summary', ?)
                WHERE id = ?
            """,
                (results_count, json.dumps(summary), job_id),
            )
        else:
            # For single page jobs, count is 1 if successful
            results_count = 1 if result.get("status") == "success" else 0

            # Update job status
            cursor.execute(
                """
                UPDATE jobs 
                SET status = 'completed', 
                    completed_at = CURRENT_TIMESTAMP,
                    results_count = ?
                WHERE id = ?
            """,
                (results_count, job_id),
            )

        conn.commit()
        conn.close()

        logger.info(f"Successfully completed scraping job {job_id} for URL: {url}")

        return {
            "job_id": job_id,
            "status": "completed",
            "url": url,
            "data": result,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Scraping job {job_id} failed: {str(e)}")

        # Update job status to failed
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE jobs 
                SET status = 'failed', 
                    completed_at = CURRENT_TIMESTAMP,
                    error_message = ?
                WHERE id = ?
            """,
                (str(e), job_id),
            )
            conn.commit()
            conn.close()
        except Exception as db_error:
            logger.error(f"Failed to update job status: {str(db_error)}")

        return {
            "job_id": job_id,
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


if __name__ == "__main__":
    # Test the scraping engine
    async def test_scraping():
        engine = ScrapingEngine()

        # Test basic scraping
        result = await engine.scrape_url("https://httpbin.org/html", "basic")
        print("Basic scraping result:", json.dumps(result, indent=2))

        # Test API scraping
        api_result = await engine.scrape_url("https://httpbin.org/json", "api")
        print("API scraping result:", json.dumps(api_result, indent=2))

    asyncio.run(test_scraping())
