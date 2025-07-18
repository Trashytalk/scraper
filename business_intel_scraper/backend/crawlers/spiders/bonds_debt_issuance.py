"""Spider scraping corporate bond and debt issuance data."""

from __future__ import annotations

import scrapy


class BondsDebtIssuanceSpider(scrapy.Spider):
    """Collect bond listings and defaults."""

    name = "bonds_debt_issuance"

    def parse(self, response: scrapy.http.Response):
        yield {}
