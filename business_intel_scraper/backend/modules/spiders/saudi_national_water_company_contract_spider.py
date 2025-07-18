"""Placeholder spider for Saudi National Water Company Contract."""

import scrapy


class SaudiNationalWaterCompanyContractSpider(scrapy.Spider):
    name = "saudi_national_water_company_contract"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
