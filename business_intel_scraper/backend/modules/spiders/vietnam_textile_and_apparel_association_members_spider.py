"""Placeholder spider for Vietnam Textile and Apparel Association Members."""

import scrapy


class VietnamTextileAndApparelAssociationMembersSpider(scrapy.Spider):
    name = "vietnam_textile_and_apparel_association_members"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
