"""Spider for Warsaw Stock Exchange ESPI EBI Filings (placeholder)."""

import scrapy


class WarsawStockExchangeEspiEbiFilingsSpider(scrapy.Spider):
    """Placeholder spider for Warsaw Stock Exchange ESPI EBI Filings."""

    name = "warsawstockexchangeespiebifilings"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
