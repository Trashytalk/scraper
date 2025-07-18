"""Placeholder spider for Dubai JAFZA Free Zone Company Directory."""

import scrapy


class DubaiJafzaFreeZoneCompanyDirectorySpider(scrapy.Spider):
    name = "dubai_jafza_free_zone_company_directory"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
