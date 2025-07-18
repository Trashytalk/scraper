"""European/Asian IPO & Delisting Spider implementation."""

import scrapy


class EuropeanAsianIpoDelistingSpider(scrapy.Spider):
    """Spider for European/Asian IPO & Delisting."""

    name = "european_asian_ipo_delisting_spider"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        pass
