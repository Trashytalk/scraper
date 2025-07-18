"""Placeholder spider for Abenson Store Locator."""

import scrapy


class AbensonStoreLocatorSpider(scrapy.Spider):
    name = "abenson_store_locator"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
