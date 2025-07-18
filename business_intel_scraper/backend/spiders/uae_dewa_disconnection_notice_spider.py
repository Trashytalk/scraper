"""Placeholder spider for UAE DEWA Disconnection Notice."""

import scrapy


class UaeDewaDisconnectionNoticeSpider(scrapy.Spider):
    name = "uae_dewa_disconnection_notice"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
