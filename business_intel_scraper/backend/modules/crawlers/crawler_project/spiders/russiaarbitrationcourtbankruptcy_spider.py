"""Spider for Russia Arbitration Court Bankruptcy (placeholder)."""

import scrapy


class RussiaArbitrationCourtBankruptcySpider(scrapy.Spider):
    """Placeholder spider for Russia Arbitration Court Bankruptcy."""

    name = "russiaarbitrationcourtbankruptcy"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
