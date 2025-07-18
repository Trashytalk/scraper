"""Placeholder spider for Thai Hotels Association Members."""

import scrapy


class ThaiHotelsAssociationMembersSpider(scrapy.Spider):
    name = "thai_hotels_association_members"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
