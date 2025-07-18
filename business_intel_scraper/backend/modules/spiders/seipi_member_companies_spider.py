"""Placeholder spider for SEIPI Member Companies."""

import scrapy


class SeipiMemberCompaniesSpider(scrapy.Spider):
    name = "seipi_member_companies"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
