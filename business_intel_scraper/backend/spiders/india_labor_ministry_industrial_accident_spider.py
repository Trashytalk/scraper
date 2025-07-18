"""Placeholder spider for India Labor Ministry Industrial Accident."""

import scrapy


class IndiaLaborMinistryIndustrialAccidentSpider(scrapy.Spider):
    name = "india_labor_ministry_industrial_accident"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
