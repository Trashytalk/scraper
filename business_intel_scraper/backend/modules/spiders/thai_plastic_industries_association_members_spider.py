"""Placeholder spider for Thai Plastic Industries Association Members."""

import scrapy


class ThaiPlasticIndustriesAssociationMembersSpider(scrapy.Spider):
    name = "thai_plastic_industries_association_members"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
