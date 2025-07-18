"""Placeholder spider for Liberia Ship Registry."""

import scrapy


class LiberiaShipRegistrySpider(scrapy.Spider):
    name = "liberia_ship_registry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
