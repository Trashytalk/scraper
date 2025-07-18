"""Placeholder spider for US CISA Cyber Incident Notification."""

import scrapy


class UsCisaCyberIncidentNotificationSpider(scrapy.Spider):
    name = "us_cisa_cyber_incident_notification"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
