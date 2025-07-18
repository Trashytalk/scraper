"""Placeholder spider for US FEC Corporate Donor."""

import scrapy


class UsFecCorporateDonorSpider(scrapy.Spider):
    name = "us_fec_corporate_donor"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
