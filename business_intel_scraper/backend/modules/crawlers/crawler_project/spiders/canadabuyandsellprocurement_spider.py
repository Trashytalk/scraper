"""Spider for Canada BuyAndSell Procurement (placeholder)."""

import scrapy


class CanadaBuyandsellProcurementSpider(scrapy.Spider):
    """Placeholder spider for Canada BuyAndSell Procurement."""

    name = "canadabuyandsellprocurement"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
