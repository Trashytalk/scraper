"""Placeholder spider for Saigon Hi-Tech Park Tenants."""

import scrapy


class SaigonHiTechParkTenantsSpider(scrapy.Spider):
    name = "saigon_hi_tech_park_tenants"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
