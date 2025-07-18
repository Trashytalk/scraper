"""Placeholder spider for BSP List of Microfinance NGOs."""

import scrapy


class BspMicrofinanceNgosSpider(scrapy.Spider):
    name = "bsp_microfinance_ngos"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
