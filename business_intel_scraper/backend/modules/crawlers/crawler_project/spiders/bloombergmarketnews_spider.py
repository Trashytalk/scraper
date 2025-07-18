"""Spider for Bloomberg Market News (placeholder)."""

import scrapy


class BloombergMarketNewsSpider(scrapy.Spider):
    """Placeholder spider for Bloomberg Market News."""

    name = "bloombergmarketnews"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
