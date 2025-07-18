"""Placeholder spider for Bank Negara Malaysia E-money Operators."""

import scrapy


class BankNegaraMalaysiaEMoneyOperatorsSpider(scrapy.Spider):
    name = "bank_negara_malaysia_e_money_operators"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
