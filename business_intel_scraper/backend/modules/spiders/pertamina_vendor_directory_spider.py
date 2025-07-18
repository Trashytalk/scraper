"""Placeholder spider for Pertamina Vendor Directory."""

import scrapy


class PertaminaVendorDirectorySpider(scrapy.Spider):
    name = "pertamina_vendor_directory"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
