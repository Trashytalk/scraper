"""Placeholder spider for IDPRO Members (Data Center Association)."""

import scrapy


class IdproMembersSpider(scrapy.Spider):
    name = "idpro_members"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
