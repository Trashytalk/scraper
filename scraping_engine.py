"""
Real Web Scraping Engine for Business Intelligence Scraper
Provides actual web scraping functionality using multiple backends
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any
from urllib.parse import urljoin
import sqlite3

import requests
from bs4 import BeautifulSoup
import re

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

    async def _basic_scraper(self, url: str, config: Dict) -> Dict[str, Any]:
        """Basic web page scraper using BeautifulSoup"""
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
                "images": self._extract_images(soup, url),
                "word_count": len(soup.get_text().split()),
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "response_time": response.elapsed.total_seconds(),
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
        self, soup: BeautifulSoup, base_url: str
    ) -> List[Dict[str, str]]:
        images = []
        for img_tag in soup.find_all("img", src=True):
            src = img_tag.get("src")
            if src:
                absolute_url = urljoin(base_url, src)
                images.append(
                    {
                        "src": absolute_url,
                        "alt": img_tag.get("alt", ""),
                        "title": img_tag.get("title", ""),
                    }
                )
        return images[:20]  # Limit to first 20 images

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
        scraper_type = job_config.get("scraper_type", "basic")
        config = job_config.get("config", {})

        if not url:
            raise ValueError("No URL provided for scraping")

        # Perform the scraping
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

        # Update job status
        cursor.execute(
            """
            UPDATE jobs 
            SET status = 'completed', 
                completed_at = CURRENT_TIMESTAMP,
                results_count = results_count + 1
            WHERE id = ?
        """,
            (job_id,),
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
