"""Placeholder spider for Singapore ELD Party Donor Registry."""

import scrapy


class SingaporeEldPartyDonorRegistrySpider(scrapy.Spider):
    name = "singapore_eld_party_donor_registry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
