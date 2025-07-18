"""Placeholder spider for Poland UODO Data Breach."""

import scrapy


class PolandUodoDataBreachSpider(scrapy.Spider):
    name = "poland_uodo_data_breach"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
