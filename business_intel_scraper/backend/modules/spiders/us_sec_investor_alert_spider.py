"""Placeholder spider for US SEC Investor Alert."""

import scrapy


class UsSecInvestorAlertSpider(scrapy.Spider):
    name = "us_sec_investor_alert"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
