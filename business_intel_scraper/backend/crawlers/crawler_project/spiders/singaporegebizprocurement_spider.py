"""Spider for Singapore GeBIZ Procurement (placeholder)."""

import scrapy


class SingaporeGebizProcurementSpider(scrapy.Spider):
    """Placeholder spider for Singapore GeBIZ Procurement."""

    name = "singaporegebizprocurement"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
