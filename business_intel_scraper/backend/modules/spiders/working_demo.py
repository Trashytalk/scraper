"""
Working demonstration spider for scraping business news and company information.
This spider showcases the framework's capabilities with a real implementation.
"""

import scrapy
from scrapy.http import Response
from typing import Generator, Dict, Any
from urllib.parse import urljoin, urlparse
import logging

logger = logging.getLogger(__name__)


class BusinessNewsSpider(scrapy.Spider):
    """
    A working spider that scrapes business news and company mentions.

    This spider demonstrates:
    - Real data extraction
    - Proper error handling
    - Following pagination
    - Extracting structured data
    - Rate limiting respect
    """

    name = "business_news_demo"
    allowed_domains = ["reuters.com"]

    # Start with Reuters business news section
    start_urls = [
        "https://www.reuters.com/business/",
    ]

    custom_settings = {
        "DOWNLOAD_DELAY": 2,  # Be respectful
        "RANDOMIZE_DOWNLOAD_DELAY": 0.5,
        "USER_AGENT": "business-intel-scraper (+https://github.com/trashytalk/scraper)",
        "ROBOTSTXT_OBEY": True,
        "CONCURRENT_REQUESTS": 1,  # Start conservative
    }

    def parse(self, response: Response) -> Generator[Dict[str, Any], None, None]:
        """Parse the main business news page."""
        try:
            # Extract article links
            article_links = response.css(
                'a[data-testid="Heading"]::attr(href)'
            ).getall()

            if not article_links:
                # Fallback to more generic selectors
                article_links = response.css("article a::attr(href)").getall()

            logger.info(f"Found {len(article_links)} article links on {response.url}")

            # Process each article
            for link in article_links[:10]:  # Limit to first 10 for demo
                if link:
                    full_url = urljoin(response.url, link)
                    yield response.follow(
                        full_url, self.parse_article, meta={"source_page": response.url}
                    )

            # Look for pagination
            next_page = response.css('a[aria-label="Next"]::attr(href)').get()
            if next_page:
                yield response.follow(next_page, self.parse)

        except Exception as e:
            logger.error(f"Error parsing {response.url}: {e}")

    def parse_article(
        self, response: Response
    ) -> Generator[Dict[str, Any], None, None]:
        """Parse individual article pages."""
        try:
            # Extract article data
            title = self._extract_title(response)
            content = self._extract_content(response)
            date = self._extract_date(response)
            author = self._extract_author(response)
            companies = self._extract_companies(content)

            if title:  # Only yield if we have at least a title
                article_data = {
                    "title": title,
                    "url": response.url,
                    "content": content,
                    "date": date,
                    "author": author,
                    "companies_mentioned": companies,
                    "domain": urlparse(response.url).netloc,
                    "source_page": response.meta.get("source_page"),
                    "scraped_at": scrapy.utils.misc.load_object("datetime.datetime")
                    .now()
                    .isoformat(),
                }

                logger.info(f"Extracted article: {title[:50]}...")
                yield article_data

        except Exception as e:
            logger.error(f"Error parsing article {response.url}: {e}")

    def _extract_title(self, response: Response) -> str:
        """Extract article title with multiple fallbacks."""
        selectors = [
            'h1[data-testid="Heading"]::text',
            "h1.ArticleHeader_headline::text",
            "h1::text",
            '[data-testid="Heading"]::text',
            ".headline::text",
            "title::text",
        ]

        for selector in selectors:
            title = response.css(selector).get()
            if title:
                return title.strip()
        return ""

    def _extract_content(self, response: Response) -> str:
        """Extract article content."""
        selectors = [
            '[data-testid="paragraph"] p::text',
            ".ArticleBody_body p::text",
            "article p::text",
            ".content p::text",
            "p::text",
        ]

        for selector in selectors:
            paragraphs = response.css(selector).getall()
            if paragraphs:
                content = " ".join(p.strip() for p in paragraphs if p.strip())
                if len(content) > 100:  # Ensure we have substantial content
                    return content
        return ""

    def _extract_date(self, response: Response) -> str:
        """Extract publication date."""
        selectors = [
            '[data-testid="AuthorByline"] time::attr(datetime)',
            "time::attr(datetime)",
            ".timestamp::attr(datetime)",
            '[data-testid="timestamp"]::text',
            ".date::text",
        ]

        for selector in selectors:
            date = response.css(selector).get()
            if date:
                return date.strip()
        return ""

    def _extract_author(self, response: Response) -> str:
        """Extract author information."""
        selectors = [
            '[data-testid="AuthorByline"] span::text',
            ".author::text",
            ".byline::text",
            '[data-testid="author"]::text',
        ]

        for selector in selectors:
            author = response.css(selector).get()
            if author:
                return author.strip()
        return ""

    def _extract_companies(self, content: str) -> list:
        """Extract company mentions from content using simple keyword matching."""
        if not content:
            return []

        # Common company indicators
        company_indicators = [
            "Inc.",
            "Corp.",
            "Corporation",
            "Company",
            "Ltd.",
            "Limited",
            "LLC",
            "LP",
            "Holdings",
            "Group",
            "Enterprises",
            "Industries",
        ]

        companies = []
        words = content.split()

        for i, word in enumerate(words):
            if any(indicator in word for indicator in company_indicators):
                # Try to get the company name (usually 1-3 words before the indicator)
                start = max(0, i - 3)
                company_phrase = " ".join(words[start : i + 1])

                # Clean up the phrase
                company_phrase = company_phrase.strip('.,!?;:"()[]{}')

                if len(company_phrase) > 5 and company_phrase not in companies:
                    companies.append(company_phrase)

        return companies[:5]  # Limit to top 5 mentions


class TechCrunchSpider(scrapy.Spider):
    """Alternative spider for TechCrunch startup news."""

    name = "techcrunch_startups"
    allowed_domains = ["techcrunch.com"]
    start_urls = ["https://techcrunch.com/category/startups/"]

    custom_settings = {
        "DOWNLOAD_DELAY": 3,
        "ROBOTSTXT_OBEY": True,
        "USER_AGENT": "business-intel-scraper (+https://github.com/trashytalk/scraper)",
    }

    def parse(self, response: Response) -> Generator[Dict[str, Any], None, None]:
        """Parse TechCrunch startup articles."""
        article_links = response.css("h2.post-block__title a::attr(href)").getall()

        for link in article_links[:5]:  # Limit for demo
            if link:
                yield response.follow(link, self.parse_article)

    def parse_article(
        self, response: Response
    ) -> Generator[Dict[str, Any], None, None]:
        """Parse TechCrunch article."""
        try:
            title = response.css("h1.article__title::text").get()
            content_paragraphs = response.css(".article-content p::text").getall()
            content = " ".join(p.strip() for p in content_paragraphs)

            if title:
                yield {
                    "title": title.strip(),
                    "url": response.url,
                    "content": content,
                    "domain": "techcrunch.com",
                    "category": "startups",
                    "scraped_at": scrapy.utils.misc.load_object("datetime.datetime")
                    .now()
                    .isoformat(),
                }
        except Exception as e:
            logger.error(f"Error parsing TechCrunch article {response.url}: {e}")
