"""Placeholder spider for EMA Licensed Electrical Contractors."""

import scrapy


class EmaLicensedElectricalContractorsSpider(scrapy.Spider):
    name = "ema_licensed_electrical_contractors"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
