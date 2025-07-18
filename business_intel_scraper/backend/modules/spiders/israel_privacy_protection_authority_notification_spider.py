"""Placeholder spider for Israel Privacy Protection Authority Notification."""

import scrapy


class IsraelPrivacyProtectionAuthorityNotificationSpider(scrapy.Spider):
    name = "israel_privacy_protection_authority_notification"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
