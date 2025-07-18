"""Placeholder spider for Panama Maritime Authority Ship Registry."""

import scrapy


class PanamaMaritimeAuthorityShipRegistrySpider(scrapy.Spider):
    name = "panama_maritime_authority_ship_registry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
