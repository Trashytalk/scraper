"""Spider for France BODACC Judicial Liquidation (placeholder)."""

import scrapy


class FranceBodaccJudicialLiquidationSpider(scrapy.Spider):
    """Placeholder spider for France BODACC Judicial Liquidation."""

    name = "francebodaccjudicialliquidation"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
