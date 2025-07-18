"""Placeholder spider for UAE JV Commercial Register."""

import scrapy


class UaeJvCommercialRegisterSpider(scrapy.Spider):
    name = "uae_jv_commercial_register"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
