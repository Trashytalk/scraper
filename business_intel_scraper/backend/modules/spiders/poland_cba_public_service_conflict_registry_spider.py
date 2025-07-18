"""Placeholder spider for Poland CBA Public Service Conflict Registry."""

import scrapy


class PolandCbaPublicServiceConflictRegistrySpider(scrapy.Spider):
    name = "poland_cba_public_service_conflict_registry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
