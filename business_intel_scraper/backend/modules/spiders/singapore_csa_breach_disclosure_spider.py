"""Placeholder spider for Singapore CSA Breach Disclosure."""

import scrapy


class SingaporeCsaBreachDisclosureSpider(scrapy.Spider):
    name = "singapore_csa_breach_disclosure"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
