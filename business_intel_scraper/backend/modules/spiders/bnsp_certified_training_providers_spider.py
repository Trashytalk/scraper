"""Placeholder spider for BNSP Certified Training Providers."""

import scrapy


class BnspCertifiedTrainingProvidersSpider(scrapy.Spider):
    name = "bnsp_certified_training_providers"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
