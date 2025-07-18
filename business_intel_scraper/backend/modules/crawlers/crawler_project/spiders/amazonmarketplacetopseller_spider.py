"""Spider for Amazon Marketplace Top Seller (placeholder)."""

import scrapy


class AmazonMarketplaceTopSellerSpider(scrapy.Spider):
    """Placeholder spider for Amazon Marketplace Top Seller."""

    name = "amazonmarketplacetopseller"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
