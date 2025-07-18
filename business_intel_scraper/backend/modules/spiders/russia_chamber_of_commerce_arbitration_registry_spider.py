"""Placeholder spider for Russia Chamber of Commerce Arbitration Registry."""

import scrapy


class RussiaChamberOfCommerceArbitrationRegistrySpider(scrapy.Spider):
    name = "russia_chamber_of_commerce_arbitration_registry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
