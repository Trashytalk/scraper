"""Spider for Saudi Arabia Government Tenders Procurement (placeholder)."""

import scrapy


class SaudiArabiaGovernmentTendersProcurementSpider(scrapy.Spider):
    """Placeholder spider for Saudi Arabia Government Tenders Procurement."""

    name = "saudiarabiagovernmenttendersprocurement"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
