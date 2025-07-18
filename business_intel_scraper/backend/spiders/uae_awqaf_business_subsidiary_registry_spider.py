"""Placeholder spider for UAE Awqaf Business Subsidiary Registry."""

import scrapy


class UaeAwqafBusinessSubsidiaryRegistrySpider(scrapy.Spider):
    name = "uae_awqaf_business_subsidiary_registry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
