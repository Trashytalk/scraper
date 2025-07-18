"""Spider for OFAC SDN List (placeholder)."""

import scrapy


class OfacSdnListSpider(scrapy.Spider):
    """Placeholder spider for OFAC SDN List."""

    name = "ofacsdnlist"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
