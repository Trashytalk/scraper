"""Placeholder spider for UAE Data Office Breach Disclosure."""

import scrapy


class UaeDataOfficeBreachDisclosureSpider(scrapy.Spider):
    name = "uae_data_office_breach_disclosure"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
