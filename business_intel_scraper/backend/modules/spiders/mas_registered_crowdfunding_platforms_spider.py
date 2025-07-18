"""Placeholder spider for MAS Registered Crowdfunding Platforms."""

import scrapy


class MasRegisteredCrowdfundingPlatformsSpider(scrapy.Spider):
    name = "mas_registered_crowdfunding_platforms"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
