"""Placeholder spider for Singapore SP Group Utility Award."""

import scrapy


class SingaporeSpGroupUtilityAwardSpider(scrapy.Spider):
    name = "singapore_sp_group_utility_award"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
