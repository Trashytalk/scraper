"""Placeholder spider for Singapore Logistics Association Member Directory."""

import scrapy


class SingaporeLogisticsAssociationMembersSpider(scrapy.Spider):
    name = "singapore_logistics_association_members"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
