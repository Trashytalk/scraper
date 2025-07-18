"""Spider for Kenya IFMIS (placeholder)."""

import scrapy


class KenyaIfmisSpider(scrapy.Spider):
    """Placeholder spider for Kenya IFMIS."""

    name = "kenyaifmis"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
