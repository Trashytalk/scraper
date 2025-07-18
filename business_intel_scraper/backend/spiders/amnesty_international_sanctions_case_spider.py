"""Placeholder spider for Amnesty International Sanctions Case."""

import scrapy


class AmnestyInternationalSanctionsCaseSpider(scrapy.Spider):
    name = "amnesty_international_sanctions_case"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
