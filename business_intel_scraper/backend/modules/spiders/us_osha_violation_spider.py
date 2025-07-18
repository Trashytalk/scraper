"""Placeholder spider for US OSHA Violation."""

import scrapy


class UsOshaViolationSpider(scrapy.Spider):
    name = "us_osha_violation"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
