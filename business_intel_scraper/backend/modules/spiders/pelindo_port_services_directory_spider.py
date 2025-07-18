"""Placeholder spider for Pelindo Port Services Directory."""

import scrapy


class PelindoPortServicesDirectorySpider(scrapy.Spider):
    name = "pelindo_port_services_directory"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
