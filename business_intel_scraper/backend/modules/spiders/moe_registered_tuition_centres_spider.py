"""Placeholder spider for MOE Registered Tuition Centres."""

import scrapy


class MoeRegisteredTuitionCentresSpider(scrapy.Spider):
    name = "moe_registered_tuition_centres"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
