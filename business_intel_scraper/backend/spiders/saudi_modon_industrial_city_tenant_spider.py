"""Placeholder spider for Saudi Modon Industrial City Tenant."""

import scrapy


class SaudiModonIndustrialCityTenantSpider(scrapy.Spider):
    name = "saudi_modon_industrial_city_tenant"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
