"""Placeholder spider for US County-Level Tax Lien Sale."""

import scrapy


class UsCountyLevelTaxLienSaleSpider(scrapy.Spider):
    name = "us_county_level_tax_lien_sale"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
