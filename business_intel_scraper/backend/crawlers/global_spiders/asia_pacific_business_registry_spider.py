"""Asia-Pacific Business Registry Spider implementation."""

import scrapy


class AsiaPacificBusinessRegistrySpider(scrapy.Spider):
    """Spider for Asia-Pacific Business Registry."""

    name = "asia_pacific_business_registry_spider"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        pass
