"""Spider for Burger King Regional Franchise (placeholder)."""

import scrapy


class BurgerKingRegionalFranchiseSpider(scrapy.Spider):
    """Placeholder spider for Burger King Regional Franchise."""

    name = "burgerkingregionalfranchise"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
