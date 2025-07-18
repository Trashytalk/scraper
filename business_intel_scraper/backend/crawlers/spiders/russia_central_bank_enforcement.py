"""Harvest sanctions, bans, and compliance notices on financial institutions."""

from __future__ import annotations

import scrapy


class RussiaCentralBankEnforcementActionSpider(scrapy.Spider):
    """Harvest sanctions, bans, and compliance notices on financial institutions."""

    name = "russiacentralbankenforcementactionspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
