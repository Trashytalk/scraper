"""Placeholder spider for DOE Electrification Projects."""

import scrapy


class DoeElectrificationProjectsSpider(scrapy.Spider):
    name = "doe_electrification_projects"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
