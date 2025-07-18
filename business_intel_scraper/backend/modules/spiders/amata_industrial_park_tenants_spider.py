"""Placeholder spider for Amata Industrial Park Tenants."""

import scrapy


class AmataIndustrialParkTenantsSpider(scrapy.Spider):
    name = "amata_industrial_park_tenants"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
