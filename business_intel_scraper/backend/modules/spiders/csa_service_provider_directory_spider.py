"""Placeholder spider for CSA Singapore Service Provider Directory."""

import scrapy


class CsaServiceProviderDirectorySpider(scrapy.Spider):
    name = "csa_service_provider_directory"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
