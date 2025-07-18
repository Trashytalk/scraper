"""Placeholder spider for EU AML Authority Sanction."""

import scrapy


class EuAmlAuthoritySanctionSpider(scrapy.Spider):
    name = "eu_aml_authority_sanction"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
