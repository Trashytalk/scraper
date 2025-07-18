"""Scrape company filings, annual reports, and insolvency actions."""

from __future__ import annotations

import scrapy


class PolandNationalCourtRegisterSpider(scrapy.Spider):
    """Scrape company filings, annual reports, and insolvency actions."""

    name = "polandnationalcourtregisterspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
