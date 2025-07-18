"""Placeholder spider for Singapore Commercial Affairs Department AML Conviction."""

import scrapy


class SingaporeCommercialAffairsDepartmentAmlConvictionSpider(scrapy.Spider):
    name = "singapore_commercial_affairs_department_aml_conviction"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
