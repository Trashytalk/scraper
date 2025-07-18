"""Spider watching commodity trading disclosures."""

from __future__ import annotations

import scrapy


class CommodityTradingSpider(scrapy.Spider):
    """Track commodity exchange listings and filings."""

    name = "commodity_trading"

    def parse(self, response: scrapy.http.Response):
        yield {}
