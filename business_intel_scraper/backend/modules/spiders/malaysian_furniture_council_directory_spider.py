"""Placeholder spider for Malaysian Furniture Council Directory."""

import scrapy


class MalaysianFurnitureCouncilDirectorySpider(scrapy.Spider):
    name = "malaysian_furniture_council_directory"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
