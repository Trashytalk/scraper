"""Placeholder spider for e27 Healthtech Startup List."""

import scrapy


class E27HealthtechStartupListSpider(scrapy.Spider):
    name = "e27_healthtech_startup_list"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
