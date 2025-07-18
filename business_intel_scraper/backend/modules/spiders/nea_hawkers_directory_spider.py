"""Placeholder spider for NEA Hawkers Directory."""

import scrapy


class NeaHawkersDirectorySpider(scrapy.Spider):
    name = "nea_hawkers_directory"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
