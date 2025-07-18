"""Placeholder spider for FMM Members (Food)."""

import scrapy


class FmmMembersFoodSpider(scrapy.Spider):
    name = "fmm_members_food"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
