"""International NGO Watch Spider implementation."""

import scrapy


class InternationalNgoWatchSpider(scrapy.Spider):
    """Spider for International NGO Watch."""

    name = "international_ngo_watch_spider"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        pass
