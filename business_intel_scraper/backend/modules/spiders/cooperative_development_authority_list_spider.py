"""Placeholder spider for Cooperative Development Authority List."""

import scrapy


class CooperativeDevelopmentAuthorityListSpider(scrapy.Spider):
    name = "cooperative_development_authority_list"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
