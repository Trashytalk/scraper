"""Spider for South Africa Chamber of Commerce (placeholder)."""

import scrapy


class SouthAfricaChamberOfCommerceSpider(scrapy.Spider):
    """Placeholder spider for South Africa Chamber of Commerce."""

    name = "southafricachamberofcommerce"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
