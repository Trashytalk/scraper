"""Global Real Estate Ownership Spider implementation."""

import scrapy


class GlobalRealEstateOwnershipSpider(scrapy.Spider):
    """Spider for Global Real Estate Ownership."""

    name = "global_real_estate_ownership_spider"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        pass
