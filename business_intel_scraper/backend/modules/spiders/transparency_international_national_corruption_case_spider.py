"""Placeholder spider for Transparency International National Corruption Case."""

import scrapy


class TransparencyInternationalNationalCorruptionCaseSpider(scrapy.Spider):
    name = "transparency_international_national_corruption_case"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
