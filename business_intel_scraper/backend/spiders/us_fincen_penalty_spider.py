"""Placeholder spider for US FinCEN Penalty."""

import scrapy


class UsFincenPenaltySpider(scrapy.Spider):
    name = "us_fincen_penalty"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
