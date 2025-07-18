"""Placeholder spider for UAE MOHRE Work Permit Registry."""

import scrapy


class UaeMohreWorkPermitRegistrySpider(scrapy.Spider):
    name = "uae_mohre_work_permit_registry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
