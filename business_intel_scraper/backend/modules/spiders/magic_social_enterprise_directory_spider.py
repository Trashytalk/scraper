"""Placeholder spider for MaGIC Social Enterprise Directory."""

import scrapy


class MagicSocialEnterpriseDirectorySpider(scrapy.Spider):
    name = "magic_social_enterprise_directory"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
