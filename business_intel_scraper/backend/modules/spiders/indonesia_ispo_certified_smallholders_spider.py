"""Placeholder spider for Indonesia ISPO Certified Smallholders."""

import scrapy


class IndonesiaIspoCertifiedSmallholdersSpider(scrapy.Spider):
    name = "indonesia_ispo_certified_smallholders"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
