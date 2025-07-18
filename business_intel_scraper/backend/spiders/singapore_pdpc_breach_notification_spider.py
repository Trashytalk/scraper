"""Placeholder spider for Singapore PDPC Breach Notification."""

import scrapy


class SingaporePdpcBreachNotificationSpider(scrapy.Spider):
    name = "singapore_pdpc_breach_notification"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
