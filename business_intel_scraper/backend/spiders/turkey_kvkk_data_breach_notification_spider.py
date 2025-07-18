"""Placeholder spider for Turkey KVKK Data Breach Notification."""

import scrapy


class TurkeyKvkkDataBreachNotificationSpider(scrapy.Spider):
    name = "turkey_kvkk_data_breach_notification"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
