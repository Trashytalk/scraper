"""Placeholder spider for Print & Media Association Singapore Members."""

import scrapy


class PrintMediaAssociationSingaporeMembersSpider(scrapy.Spider):
    name = "print_media_association_singapore_members"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
