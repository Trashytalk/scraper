"""Spider for Interpol Red Notice Business Links (placeholder)."""

import scrapy


class InterpolRedNoticeBusinessLinksSpider(scrapy.Spider):
    """Placeholder spider for Interpol Red Notice Business Links."""

    name = "interpolrednoticebusinesslinks"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
