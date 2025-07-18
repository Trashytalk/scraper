"""Spider for British Chamber of Commerce Regional (placeholder)."""

import scrapy


class BritishChamberOfCommerceRegionalSpider(scrapy.Spider):
    """Placeholder spider for British Chamber of Commerce Regional."""

    name = "britishchamberofcommerceregional"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
