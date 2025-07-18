"""Placeholder spider for FAA US Aircraft Owner."""

import scrapy


class FaaUsAircraftOwnerSpider(scrapy.Spider):
    name = "faa_us_aircraft_owner"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
