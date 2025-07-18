"""Placeholder spider for Philippines Bureau of Immigration Accredited Agents."""

import scrapy


class PhilippinesBureauImmigrationAccreditedAgentsSpider(scrapy.Spider):
    name = "philippines_bureau_immigration_accredited_agents"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
