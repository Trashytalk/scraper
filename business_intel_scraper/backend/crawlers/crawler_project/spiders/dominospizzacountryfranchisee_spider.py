"""Spider for Dominos Pizza Country Franchisee (placeholder)."""

import scrapy


class DominosPizzaCountryFranchiseeSpider(scrapy.Spider):
    """Placeholder spider for Dominos Pizza Country Franchisee."""

    name = "dominospizzacountryfranchisee"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
