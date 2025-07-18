"""Placeholder spider for Poland PIP Safety Violation."""

import scrapy


class PolandPipSafetyViolationSpider(scrapy.Spider):
    name = "poland_pip_safety_violation"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
