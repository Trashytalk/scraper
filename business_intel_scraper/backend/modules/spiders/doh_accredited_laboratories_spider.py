"""Placeholder spider for DOH Accredited Laboratories."""

import scrapy


class DohAccreditedLaboratoriesSpider(scrapy.Spider):
    name = "doh_accredited_laboratories"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
