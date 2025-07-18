"""Spider collecting supplier/buyer relationship data."""

from __future__ import annotations

import scrapy


class SupplierBuyerSpider(scrapy.Spider):
    """Scrape published supplier and buyer lists."""

    name = "supplier_buyer"

    def parse(self, response: scrapy.http.Response):
        yield {}
