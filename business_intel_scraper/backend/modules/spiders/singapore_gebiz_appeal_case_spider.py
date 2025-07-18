"""Placeholder spider for Singapore GeBIZ Appeal Case."""

import scrapy


class SingaporeGebizAppealCaseSpider(scrapy.Spider):
    name = "singapore_gebiz_appeal_case"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
