"""Placeholder spider for Saudi PIF Partnership Announcement."""

import scrapy


class SaudiPifPartnershipAnnouncementSpider(scrapy.Spider):
    name = "saudi_pif_partnership_announcement"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
