"""Placeholder spider for South Africa FSCA Warning."""

import scrapy


class SouthAfricaFscaWarningSpider(scrapy.Spider):
    name = "south_africa_fsca_warning"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
