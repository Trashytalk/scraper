"""Placeholder spider for US Federal Post-Government Employment Disclosure."""

import scrapy


class UsFederalPostGovernmentEmploymentDisclosureSpider(scrapy.Spider):
    name = "us_federal_post_government_employment_disclosure"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
