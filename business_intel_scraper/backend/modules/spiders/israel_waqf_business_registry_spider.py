"""Placeholder spider for Israel Waqf Business Registry."""

import scrapy


class IsraelWaqfBusinessRegistrySpider(scrapy.Spider):
    name = "israel_waqf_business_registry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
