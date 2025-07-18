"""Placeholder spider for Vietnam Pharmacy Chain List (Ministry of Health)."""

import scrapy


class VietnamPharmacyChainListSpider(scrapy.Spider):
    name = "vietnam_pharmacy_chain_list"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
