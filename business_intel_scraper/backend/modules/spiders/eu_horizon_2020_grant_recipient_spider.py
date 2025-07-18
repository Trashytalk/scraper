"""Placeholder spider for EU Horizon 2020 Grant Recipient."""

import scrapy


class EuHorizon2020GrantRecipientSpider(scrapy.Spider):
    name = "eu_horizon_2020_grant_recipient"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
