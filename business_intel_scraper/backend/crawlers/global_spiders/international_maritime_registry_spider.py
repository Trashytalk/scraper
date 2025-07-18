"""International Maritime Registry Spider implementation."""

import scrapy


class InternationalMaritimeRegistrySpider(scrapy.Spider):
    """Spider for International Maritime Registry."""

    name = "international_maritime_registry_spider"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        pass
