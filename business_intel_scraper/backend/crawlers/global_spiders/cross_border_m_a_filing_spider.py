"""Cross-Border M&A Filing Spider implementation."""

import scrapy


class CrossBorderMAFilingSpider(scrapy.Spider):
    """Spider for Cross-Border M&A Filing."""

    name = "cross_border_m_a_filing_spider"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        pass
