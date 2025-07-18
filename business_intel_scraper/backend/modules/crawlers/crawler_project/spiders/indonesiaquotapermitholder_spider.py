"""Spider for Indonesia Quota Permit Holder (placeholder)."""

import scrapy


class IndonesiaQuotaPermitHolderSpider(scrapy.Spider):
    """Placeholder spider for Indonesia Quota Permit Holder."""

    name = "indonesiaquotapermitholder"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
