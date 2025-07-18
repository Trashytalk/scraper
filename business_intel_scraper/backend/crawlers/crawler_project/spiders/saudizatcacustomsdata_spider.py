"""Spider for Saudi ZATCA Customs Data (placeholder)."""

import scrapy


class SaudiZatcaCustomsDataSpider(scrapy.Spider):
    """Placeholder spider for Saudi ZATCA Customs Data."""

    name = "saudizatcacustomsdata"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
