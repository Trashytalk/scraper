"""Spider for Singapore Chinese Chamber of Commerce (placeholder)."""

import scrapy


class SingaporeChineseChamberOfCommerceSpider(scrapy.Spider):
    """Placeholder spider for Singapore Chinese Chamber of Commerce."""

    name = "singaporechinesechamberofcommerce"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
