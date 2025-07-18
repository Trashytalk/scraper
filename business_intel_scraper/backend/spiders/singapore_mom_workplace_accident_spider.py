"""Placeholder spider for Singapore MOM Workplace Accident."""

import scrapy


class SingaporeMomWorkplaceAccidentSpider(scrapy.Spider):
    name = "singapore_mom_workplace_accident"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
