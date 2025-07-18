"""Placeholder spider for Malaysia Bursa ESG Reporting."""

import scrapy


class MalaysiaBursaEsgReportingSpider(scrapy.Spider):
    name = "malaysia_bursa_esg_reporting"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
