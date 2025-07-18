"""Spider for The Business Times Corporate News (placeholder)."""

import scrapy


class TheBusinessTimesCorporateNewsSpider(scrapy.Spider):
    """Placeholder spider for The Business Times Corporate News."""

    name = "thebusinesstimescorporatenews"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
