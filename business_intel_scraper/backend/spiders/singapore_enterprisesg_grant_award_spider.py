"""Placeholder spider for Singapore EnterpriseSG Grant Award."""

import scrapy


class SingaporeEnterprisesgGrantAwardSpider(scrapy.Spider):
    name = "singapore_enterprisesg_grant_award"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
