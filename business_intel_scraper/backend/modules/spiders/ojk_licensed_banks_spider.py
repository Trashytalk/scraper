"""Placeholder spider for OJK Licensed Banks."""

import scrapy


class OjkLicensedBanksSpider(scrapy.Spider):
    name = "ojk_licensed_banks"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
