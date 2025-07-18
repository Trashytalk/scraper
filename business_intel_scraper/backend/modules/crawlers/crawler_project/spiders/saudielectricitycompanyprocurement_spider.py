"""Spider for Saudi Electricity Company Procurement (placeholder)."""

import scrapy


class SaudiElectricityCompanyProcurementSpider(scrapy.Spider):
    """Placeholder spider for Saudi Electricity Company Procurement."""

    name = "saudielectricitycompanyprocurement"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
