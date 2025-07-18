"""Spider for Poland Ministry of Finance Tax Debtor List (placeholder)."""

import scrapy


class PolandMinistryOfFinanceTaxDebtorListSpider(scrapy.Spider):
    """Placeholder spider for Poland Ministry of Finance Tax Debtor List."""

    name = "polandministryoffinancetaxdebtorlist"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
