"""African Corporate Registry Spider implementation."""

import scrapy


class AfricanCorporateRegistrySpider(scrapy.Spider):
    """Spider for African Corporate Registry."""

    name = "african_corporate_registry_spider"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        pass
