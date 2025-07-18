"""Placeholder spider for Global Witness Industry Report."""

import scrapy


class GlobalWitnessIndustryReportSpider(scrapy.Spider):
    name = "global_witness_industry_report"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
