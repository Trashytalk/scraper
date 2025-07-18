"""Placeholder spider for Malaysia MIDA Partnership Registry."""

import scrapy


class MalaysiaMidaPartnershipRegistrySpider(scrapy.Spider):
    name = "malaysia_mida_partnership_registry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
