"""Placeholder spider for AsiaWorks Talent Agency Directory."""

import scrapy


class AsiaworksTalentAgencyDirectorySpider(scrapy.Spider):
    name = "asiaworks_talent_agency_directory"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
