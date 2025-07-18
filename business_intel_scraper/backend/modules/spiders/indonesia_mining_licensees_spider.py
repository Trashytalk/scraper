"""Placeholder spider for Ministry of Energy and Mineral Resources Mining Licensees."""

import scrapy


class IndonesiaMiningLicenseesSpider(scrapy.Spider):
    name = "indonesia_mining_licensees"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
