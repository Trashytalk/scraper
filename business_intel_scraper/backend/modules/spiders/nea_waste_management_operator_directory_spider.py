"""Placeholder spider for NEA Waste Management Operator Directory."""

import scrapy


class NeaWasteManagementOperatorDirectorySpider(scrapy.Spider):
    name = "nea_waste_management_operator_directory"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
