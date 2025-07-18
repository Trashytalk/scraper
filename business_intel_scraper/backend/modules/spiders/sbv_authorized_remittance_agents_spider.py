"""Placeholder spider for SBV Authorized Remittance Agents."""

import scrapy


class SbvAuthorizedRemittanceAgentsSpider(scrapy.Spider):
    name = "sbv_authorized_remittance_agents"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
