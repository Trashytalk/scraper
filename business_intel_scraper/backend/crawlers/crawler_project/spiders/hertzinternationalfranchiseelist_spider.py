"""Spider for Hertz International Franchisee List (placeholder)."""

import scrapy


class HertzInternationalFranchiseeListSpider(scrapy.Spider):
    """Placeholder spider for Hertz International Franchisee List."""

    name = "hertzinternationalfranchiseelist"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
