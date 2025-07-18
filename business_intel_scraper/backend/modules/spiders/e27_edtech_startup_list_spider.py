"""Placeholder spider for e27 Edtech Startup List."""

import scrapy


class E27EdtechStartupListSpider(scrapy.Spider):
    name = "e27_edtech_startup_list"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
