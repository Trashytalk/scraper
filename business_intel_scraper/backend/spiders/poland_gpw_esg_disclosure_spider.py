"""Placeholder spider for Poland GPW ESG Disclosure."""

import scrapy


class PolandGpwEsgDisclosureSpider(scrapy.Spider):
    name = "poland_gpw_esg_disclosure"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
