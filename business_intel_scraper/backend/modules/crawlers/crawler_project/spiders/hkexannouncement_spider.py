"""Spider for HKEX Announcement (placeholder)."""

import scrapy


class HkexAnnouncementSpider(scrapy.Spider):
    """Placeholder spider for HKEX Announcement."""

    name = "hkexannouncement"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
