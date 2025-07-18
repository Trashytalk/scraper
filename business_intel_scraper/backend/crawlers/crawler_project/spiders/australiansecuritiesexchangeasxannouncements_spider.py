"""Spider for Australian Securities Exchange ASX Announcements (placeholder)."""

import scrapy


class AustralianSecuritiesExchangeAsxAnnouncementsSpider(scrapy.Spider):
    """Placeholder spider for Australian Securities Exchange ASX Announcements."""

    name = "australiansecuritiesexchangeasxannouncements"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
