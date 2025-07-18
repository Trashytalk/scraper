"""Placeholder spider for Azerbaijan e-Resident Registry."""

import scrapy


class AzerbaijanEResidentRegistrySpider(scrapy.Spider):
    name = "azerbaijan_e_resident_registry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
