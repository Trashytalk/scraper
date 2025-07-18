"""Spider for China National Enterprise Credit Information Publicity System.

This is a placeholder implementation.
"""

import scrapy


class ChinaNationalEnterpriseCreditInformationPublicitySystemSpider(scrapy.Spider):
    """Placeholder spider for the national enterprise publicity system."""

    name = "chinanationalenterprisecreditinformationpublicitysystem"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
