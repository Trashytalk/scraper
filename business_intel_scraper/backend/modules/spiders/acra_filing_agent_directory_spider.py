"""Placeholder spider for ACRA Filing Agent Directory."""

import scrapy


class AcraFilingAgentDirectorySpider(scrapy.Spider):
    name = "acra_filing_agent_directory"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
