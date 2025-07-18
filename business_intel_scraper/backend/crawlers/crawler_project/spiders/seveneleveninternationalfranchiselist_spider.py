"""Spider for 7 Eleven International Franchise List (placeholder)."""

import scrapy


class SevenElevenInternationalFranchiseListSpider(scrapy.Spider):
    """Placeholder spider for 7 Eleven International Franchise List."""

    name = "seveneleveninternationalfranchiselist"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
