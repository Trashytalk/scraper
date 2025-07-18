"""Spider for Saudi GOSI Benefit Fraud (placeholder)."""

import scrapy


class SaudiGosiBenefitFraudSpider(scrapy.Spider):
    """Placeholder spider for Saudi GOSI Benefit Fraud."""

    name = "saudigosibenefitfraud"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
