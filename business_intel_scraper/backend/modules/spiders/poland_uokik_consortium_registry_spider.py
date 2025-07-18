"""Placeholder spider for Poland UOKiK Consortium Registry."""

import scrapy


class PolandUokikConsortiumRegistrySpider(scrapy.Spider):
    name = "poland_uokik_consortium_registry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
