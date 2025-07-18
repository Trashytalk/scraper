"""Placeholder spider for ASME Digital Agency Directory."""

import scrapy


class AsmeDigitalAgencyDirectorySpider(scrapy.Spider):
    name = "asme_digital_agency_directory"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
