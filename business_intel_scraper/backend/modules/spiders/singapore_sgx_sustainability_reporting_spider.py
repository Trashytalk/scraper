"""Placeholder spider for Singapore SGX Sustainability Reporting."""

import scrapy


class SingaporeSgxSustainabilityReportingSpider(scrapy.Spider):
    name = "singapore_sgx_sustainability_reporting"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
