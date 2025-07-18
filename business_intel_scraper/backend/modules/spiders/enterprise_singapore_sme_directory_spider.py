"""Placeholder spider for Enterprise Singapore SME Directory."""

import scrapy


class EnterpriseSingaporeSmeDirectorySpider(scrapy.Spider):
    name = "enterprise_singapore_sme_directory"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
