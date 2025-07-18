"""Scrape penalties and supervisory actions on local banks/businesses."""

from __future__ import annotations

import scrapy


class LebanonBankingControlCommissionSpider(scrapy.Spider):
    """Scrape penalties and supervisory actions on local banks/businesses."""

    name = "lebanonbankingcontrolcommissionspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
