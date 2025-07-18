"""Placeholder spider for Singapore SLA Land Repossession."""

import scrapy


class SingaporeSlaLandRepossessionSpider(scrapy.Spider):
    name = "singapore_sla_land_repossession"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
