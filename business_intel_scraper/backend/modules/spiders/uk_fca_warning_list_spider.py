"""Placeholder spider for UK FCA Warning List."""

import scrapy


class UkFcaWarningListSpider(scrapy.Spider):
    name = "uk_fca_warning_list"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
