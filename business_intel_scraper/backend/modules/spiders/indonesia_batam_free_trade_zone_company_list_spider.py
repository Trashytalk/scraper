"""Placeholder spider for Indonesia Batam Free Trade Zone Company List."""

import scrapy


class IndonesiaBatamFreeTradeZoneCompanyListSpider(scrapy.Spider):
    name = "indonesia_batam_free_trade_zone_company_list"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
