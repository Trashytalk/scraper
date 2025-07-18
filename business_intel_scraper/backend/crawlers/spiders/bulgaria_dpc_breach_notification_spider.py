from __future__ import annotations

import scrapy


class BulgariaDPCBreachNotificationSpider(scrapy.Spider):
    """Bulgaria Data Protection Commission breach notifications."""

    name = "bulgaria_dpc_breach_notification"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
