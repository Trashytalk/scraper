"""Placeholder spider for Poland Civil Aviation Authority Aircraft Registry."""

import scrapy


class PolandCivilAviationAuthorityAircraftRegistrySpider(scrapy.Spider):
    name = "poland_civil_aviation_authority_aircraft_registry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
