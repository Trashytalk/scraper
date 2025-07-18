"""Placeholder spider for Poland National Chamber Mediation Registry."""

import scrapy


class PolandNationalChamberMediationRegistrySpider(scrapy.Spider):
    name = "poland_national_chamber_mediation_registry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
