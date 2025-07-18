"""Placeholder spider for Poland NASK Cyber Event Notification."""

import scrapy


class PolandNaskCyberEventNotificationSpider(scrapy.Spider):
    name = "poland_nask_cyber_event_notification"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
