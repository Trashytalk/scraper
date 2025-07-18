"""Placeholder spider for Singapore Restaurant Directory."""

import scrapy


class SingaporeRestaurantDirectorySpider(scrapy.Spider):
    name = "singapore_restaurant_directory"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
