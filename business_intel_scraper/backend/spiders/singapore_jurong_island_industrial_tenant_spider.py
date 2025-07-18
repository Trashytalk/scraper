"""Placeholder spider for Singapore Jurong Island Industrial Tenant."""

import scrapy


class SingaporeJurongIslandIndustrialTenantSpider(scrapy.Spider):
    name = "singapore_jurong_island_industrial_tenant"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
