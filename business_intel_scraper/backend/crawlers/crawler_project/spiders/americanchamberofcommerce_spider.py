"""Spider for American Chamber of Commerce (placeholder)."""

import scrapy


class AmericanChamberOfCommerceSpider(scrapy.Spider):
    """Placeholder spider for American Chamber of Commerce."""

    name = "americanchamberofcommerce"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
