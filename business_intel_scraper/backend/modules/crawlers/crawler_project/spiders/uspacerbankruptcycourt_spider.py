"""Spider for US PACER Bankruptcy Court (placeholder)."""

import scrapy


class UsPacerBankruptcyCourtSpider(scrapy.Spider):
    """Placeholder spider for US PACER Bankruptcy Court."""

    name = "uspacerbankruptcycourt"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
