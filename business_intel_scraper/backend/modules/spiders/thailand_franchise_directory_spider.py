"""Placeholder spider for Thailand Franchise Directory."""

import scrapy


class ThailandFranchiseDirectorySpider(scrapy.Spider):
    name = "thailand_franchise_directory"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
