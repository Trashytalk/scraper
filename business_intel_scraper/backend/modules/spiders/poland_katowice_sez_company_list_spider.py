"""Placeholder spider for Poland Katowice SEZ Company List."""

import scrapy


class PolandKatowiceSezCompanyListSpider(scrapy.Spider):
    name = "poland_katowice_sez_company_list"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
