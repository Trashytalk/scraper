"""Placeholder spider for Thai Security Association Members."""

import scrapy


class ThaiSecurityAssociationMembersSpider(scrapy.Spider):
    name = "thai_security_association_members"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
