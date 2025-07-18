"""Placeholder spider for Israel INCD Cyber Incident Report."""

import scrapy


class IsraelIncdCyberIncidentReportSpider(scrapy.Spider):
    name = "israel_incd_cyber_incident_report"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
