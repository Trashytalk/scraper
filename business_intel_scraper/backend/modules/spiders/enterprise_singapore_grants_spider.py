"""Placeholder spider for Enterprise Singapore Grants."""

import scrapy


class EnterpriseSingaporeGrantsSpider(scrapy.Spider):
    name = "enterprise_singapore_grants"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
