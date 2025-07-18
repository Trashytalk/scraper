"""Spider for SGXNet Company Announcements (placeholder)."""

import scrapy


class SgxnetCompanyAnnouncementsSpider(scrapy.Spider):
    """Placeholder spider for SGXNet Company Announcements."""

    name = "sgxnetcompanyannouncements"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
