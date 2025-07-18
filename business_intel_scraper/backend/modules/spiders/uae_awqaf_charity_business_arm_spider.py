"""Placeholder spider for UAE Awqaf Charity Business Arm."""

import scrapy


class UaeAwqafCharityBusinessArmSpider(scrapy.Spider):
    name = "uae_awqaf_charity_business_arm"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
