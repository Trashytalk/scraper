"""Spider for USPTO Trademark Patent (placeholder)."""

import scrapy


class UsptoTrademarkPatentSpider(scrapy.Spider):
    """Placeholder spider for USPTO Trademark Patent."""

    name = "usptotrademarkpatent"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
