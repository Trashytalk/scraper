"""Placeholder spider for UAE CERT Notification."""

import scrapy


class UaeCertNotificationSpider(scrapy.Spider):
    name = "uae_cert_notification"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
