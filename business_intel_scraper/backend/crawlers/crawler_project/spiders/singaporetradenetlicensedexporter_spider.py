"""Spider for Singapore TradeNet Licensed Exporter (placeholder)."""

import scrapy


class SingaporeTradenetLicensedExporterSpider(scrapy.Spider):
    """Placeholder spider for Singapore TradeNet Licensed Exporter."""

    name = "singaporetradenetlicensedexporter"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
