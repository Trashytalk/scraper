"""Placeholder spider for UAE GCAA Aircraft Registry."""

import scrapy


class UaeGcaaAircraftRegistrySpider(scrapy.Spider):
    name = "uae_gcaa_aircraft_registry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
