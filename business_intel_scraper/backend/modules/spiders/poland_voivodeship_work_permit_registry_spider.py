"""Placeholder spider for Poland Voivodeship Work Permit Registry."""

import scrapy


class PolandVoivodeshipWorkPermitRegistrySpider(scrapy.Spider):
    name = "poland_voivodeship_work_permit_registry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
