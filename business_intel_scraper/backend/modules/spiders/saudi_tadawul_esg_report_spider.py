"""Placeholder spider for Saudi Tadawul ESG Report."""

import scrapy


class SaudiTadawulEsgReportSpider(scrapy.Spider):
    name = "saudi_tadawul_esg_report"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
