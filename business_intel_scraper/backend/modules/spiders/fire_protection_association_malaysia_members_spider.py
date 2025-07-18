"""Placeholder spider for Fire Protection Association Malaysia Members."""

import scrapy


class FireProtectionAssociationMalaysiaMembersSpider(scrapy.Spider):
    name = "fire_protection_association_malaysia_members"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
