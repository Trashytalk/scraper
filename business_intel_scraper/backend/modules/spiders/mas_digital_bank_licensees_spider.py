"""Placeholder spider for MAS Digital Bank Licensees."""

import scrapy


class MasDigitalBankLicenseesSpider(scrapy.Spider):
    name = "mas_digital_bank_licensees"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
