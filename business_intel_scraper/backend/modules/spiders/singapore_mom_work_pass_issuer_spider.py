"""Placeholder spider for Singapore MOM Work Pass Issuer."""

import scrapy


class SingaporeMomWorkPassIssuerSpider(scrapy.Spider):
    name = "singapore_mom_work_pass_issuer"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
