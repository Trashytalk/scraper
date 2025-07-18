"""Non-US Patent & Trademark Registry Spider implementation."""

import scrapy


class NonUsPatentTrademarkRegistrySpider(scrapy.Spider):
    """Spider for Non-US Patent & Trademark Registry."""

    name = "non_us_patent_trademark_registry_spider"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        pass
