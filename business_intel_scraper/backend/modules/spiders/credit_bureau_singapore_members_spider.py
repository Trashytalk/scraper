"""Placeholder spider for Credit Bureau Singapore Members."""

import scrapy


class CreditBureauSingaporeMembersSpider(scrapy.Spider):
    name = "credit_bureau_singapore_members"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
