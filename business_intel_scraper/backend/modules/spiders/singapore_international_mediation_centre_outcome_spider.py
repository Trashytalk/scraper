"""Placeholder spider for Singapore International Mediation Centre Outcome."""

import scrapy


class SingaporeInternationalMediationCentreOutcomeSpider(scrapy.Spider):
    name = "singapore_international_mediation_centre_outcome"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
