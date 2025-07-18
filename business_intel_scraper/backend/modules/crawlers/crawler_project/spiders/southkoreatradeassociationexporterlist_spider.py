"""Spider for South Korea Trade Association Exporter List (placeholder)."""

import scrapy


class SouthKoreaTradeAssociationExporterListSpider(scrapy.Spider):
    """Placeholder spider for South Korea Trade Association Exporter List."""

    name = "southkoreatradeassociationexporterlist"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
