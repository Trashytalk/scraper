"""Placeholder spider for UAE MOHRE Safety Incident."""

import scrapy


class UaeMohreSafetyIncidentSpider(scrapy.Spider):
    name = "uae_mohre_safety_incident"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
