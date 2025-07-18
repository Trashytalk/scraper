"""Placeholder spider for US AAA Arbitration Award."""

import scrapy


class UsAaaArbitrationAwardSpider(scrapy.Spider):
    name = "us_aaa_arbitration_award"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
