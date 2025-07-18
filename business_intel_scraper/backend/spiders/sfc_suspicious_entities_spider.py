"""Placeholder spider for SFC Suspicious Entities."""

import scrapy


class SfcSuspiciousEntitiesSpider(scrapy.Spider):
    name = "sfc_suspicious_entities"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
