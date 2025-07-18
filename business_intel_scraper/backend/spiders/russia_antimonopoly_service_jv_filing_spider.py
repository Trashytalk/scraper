"""Placeholder spider for Russia Antimonopoly Service JV Filing."""

import scrapy


class RussiaAntimonopolyServiceJvFilingSpider(scrapy.Spider):
    name = "russia_antimonopoly_service_jv_filing"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
