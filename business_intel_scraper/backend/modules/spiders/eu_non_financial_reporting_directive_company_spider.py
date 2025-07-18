"""Placeholder spider for EU Non-Financial Reporting Directive Company."""

import scrapy


class EuNonFinancialReportingDirectiveCompanySpider(scrapy.Spider):
    name = "eu_non_financial_reporting_directive_company"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
