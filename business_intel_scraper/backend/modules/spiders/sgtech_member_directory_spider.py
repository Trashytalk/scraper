"""Placeholder spider for SGTech Member Directory."""

import scrapy


class SgtechMemberDirectorySpider(scrapy.Spider):
    name = "sgtech_member_directory"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
