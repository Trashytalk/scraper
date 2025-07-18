"""International E-Commerce Marketplace Spider implementation."""

import scrapy


class InternationalECommerceMarketplaceSpider(scrapy.Spider):
    """Spider for International E-Commerce Marketplace."""

    name = "international_e_commerce_marketplace_spider"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        pass
