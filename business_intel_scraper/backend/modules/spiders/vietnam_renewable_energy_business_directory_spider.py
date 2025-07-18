"""Placeholder spider for Vietnam Renewable Energy Business Directory."""

import scrapy


class VietnamRenewableEnergyBusinessDirectorySpider(scrapy.Spider):
    name = "vietnam_renewable_energy_business_directory"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
