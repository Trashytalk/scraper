"""Placeholder spider for MAS Investor Alert List."""

import scrapy


class MasInvestorAlertListSpider(scrapy.Spider):
    name = "mas_investor_alert_list"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
