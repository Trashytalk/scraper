"""Placeholder spider for Singapore Registry of Ships."""

import scrapy


class SingaporeRegistryOfShipsSpider(scrapy.Spider):
    name = "singapore_registry_of_ships"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
