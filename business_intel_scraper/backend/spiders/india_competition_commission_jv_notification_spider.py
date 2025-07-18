"""Placeholder spider for India Competition Commission JV Notification."""

import scrapy


class IndiaCompetitionCommissionJvNotificationSpider(scrapy.Spider):
    name = "india_competition_commission_jv_notification"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
