"""Placeholder spider for Russia ICAC Arbitration Award."""

import scrapy


class RussiaIcacArbitrationAwardSpider(scrapy.Spider):
    name = "russia_icac_arbitration_award"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
