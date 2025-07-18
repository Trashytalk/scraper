"""Track corporate registrations and annual filings."""

from __future__ import annotations

import scrapy


class JordanIndustryAndTradeCompanySpider(scrapy.Spider):
    """Track corporate registrations and annual filings."""

    name = "jordanindustryandtradecompanyspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
