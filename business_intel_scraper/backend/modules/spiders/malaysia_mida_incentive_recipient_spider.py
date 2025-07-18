"""Placeholder spider for Malaysia MIDA Incentive Recipient."""

import scrapy


class MalaysiaMidaIncentiveRecipientSpider(scrapy.Spider):
    name = "malaysia_mida_incentive_recipient"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
