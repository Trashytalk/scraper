"""Spider for WSJ SEC Filings Watch (placeholder)."""

import scrapy


class WsjSecFilingsWatchSpider(scrapy.Spider):
    """Placeholder spider for WSJ SEC Filings Watch."""

    name = "wsjsecfilingswatch"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
