"""Spider monitoring bankruptcy asset sale announcements."""

from __future__ import annotations

import scrapy


class BankruptcyAssetSaleSpider(scrapy.Spider):
    """Identify distressed M&A opportunities."""

    name = "bankruptcy_asset_sale"

    def parse(self, response: scrapy.http.Response):
        yield {}
