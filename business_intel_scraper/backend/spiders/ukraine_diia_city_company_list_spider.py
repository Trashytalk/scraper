"""Placeholder spider for Ukraine Diia City Company List."""

import scrapy


class UkraineDiiaCityCompanyListSpider(scrapy.Spider):
    name = "ukraine_diia_city_company_list"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
