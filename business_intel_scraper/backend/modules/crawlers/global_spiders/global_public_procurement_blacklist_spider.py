"""Global Public Procurement Blacklist Spider implementation."""

import scrapy


class GlobalPublicProcurementBlacklistSpider(scrapy.Spider):
    """Spider for Global Public Procurement Blacklist."""

    name = "global_public_procurement_blacklist_spider"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        pass
