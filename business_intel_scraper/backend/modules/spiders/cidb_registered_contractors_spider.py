"""Placeholder spider for CIDB Registered Contractors."""

import scrapy


class CidbRegisteredContractorsSpider(scrapy.Spider):
    name = "cidb_registered_contractors"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
