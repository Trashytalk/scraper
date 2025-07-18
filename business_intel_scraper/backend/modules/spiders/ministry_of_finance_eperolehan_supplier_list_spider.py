"""Placeholder spider for Ministry of Finance ePerolehan Supplier List."""

import scrapy


class MinistryOfFinanceEperolehanSupplierListSpider(scrapy.Spider):
    name = "ministry_of_finance_eperolehan_supplier_list"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
