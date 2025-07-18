"""Spider for CNIPA Patent Trademark (placeholder)."""

import scrapy


class CnipaPatentTrademarkSpider(scrapy.Spider):
    """Placeholder spider for CNIPA Patent Trademark."""

    name = "cnipapatenttrademark"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
