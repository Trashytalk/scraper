"""Placeholder spider for Russia Ministry of Justice NGO Business Tie."""

import scrapy


class RussiaMinistryOfJusticeNgoBusinessTieSpider(scrapy.Spider):
    name = "russia_ministry_of_justice_ngo_business_tie"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
