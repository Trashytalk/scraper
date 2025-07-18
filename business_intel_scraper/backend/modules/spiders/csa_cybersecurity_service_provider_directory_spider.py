"""Placeholder spider for CSA Cybersecurity Service Provider Directory."""

import scrapy


class CsaCybersecurityServiceProviderDirectorySpider(scrapy.Spider):
    name = "csa_cybersecurity_service_provider_directory"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
