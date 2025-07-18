"""Placeholder spider for HDB Registered Renovation Contractors."""

import scrapy


class HdbRegisteredRenovationContractorsSpider(scrapy.Spider):
    name = "hdb_registered_renovation_contractors"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
