"""Spider for Reuters Business Headline (placeholder)."""

import scrapy


class ReutersBusinessHeadlineSpider(scrapy.Spider):
    """Placeholder spider for Reuters Business Headline."""

    name = "reutersbusinessheadline"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
