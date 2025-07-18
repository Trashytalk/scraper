"""Placeholder spider for Vietcombank SME Lending."""

import scrapy


class VietcombankSmeLendingSpider(scrapy.Spider):
    name = "vietcombank_sme_lending"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
