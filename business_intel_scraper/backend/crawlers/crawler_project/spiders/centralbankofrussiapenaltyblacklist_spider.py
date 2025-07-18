"""Spider for Central Bank of Russia Penalty Blacklist (placeholder)."""

import scrapy


class CentralBankOfRussiaPenaltyBlacklistSpider(scrapy.Spider):
    """Placeholder spider for Central Bank of Russia Penalty Blacklist."""

    name = "centralbankofrussiapenaltyblacklist"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
