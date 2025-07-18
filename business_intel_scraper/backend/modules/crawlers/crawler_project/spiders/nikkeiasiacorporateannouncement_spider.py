"""Spider for Nikkei Asia Corporate Announcement (placeholder)."""

import scrapy


class NikkeiAsiaCorporateAnnouncementSpider(scrapy.Spider):
    """Placeholder spider for Nikkei Asia Corporate Announcement."""

    name = "nikkeiasiacorporateannouncement"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
