"""Placeholder spider for Saudi FIU AML Enforcement."""

import scrapy


class SaudiFiuAmlEnforcementSpider(scrapy.Spider):
    name = "saudi_fiu_aml_enforcement"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
