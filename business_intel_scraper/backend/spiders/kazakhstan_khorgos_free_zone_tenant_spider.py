"""Placeholder spider for Kazakhstan Khorgos Free Zone Tenant."""

import scrapy


class KazakhstanKhorgosFreeZoneTenantSpider(scrapy.Spider):
    name = "kazakhstan_khorgos_free_zone_tenant"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
