"""Placeholder spider for Human Rights Watch Business Involvement."""

import scrapy


class HumanRightsWatchBusinessInvolvementSpider(scrapy.Spider):
    name = "human_rights_watch_business_involvement"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
