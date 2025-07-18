"""Placeholder spider for Shopee Seller Centre."""

import scrapy


class ShopeeSellerCentreSpider(scrapy.Spider):
    name = "shopee_seller_centre"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
