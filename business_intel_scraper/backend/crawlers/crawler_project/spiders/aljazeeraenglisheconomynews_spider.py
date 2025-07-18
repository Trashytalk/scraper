"""Spider for Al Jazeera English Economy News (placeholder)."""

import scrapy


class AlJazeeraEnglishEconomyNewsSpider(scrapy.Spider):
    """Placeholder spider for Al Jazeera English Economy News."""

    name = "aljazeeraenglisheconomynews"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
