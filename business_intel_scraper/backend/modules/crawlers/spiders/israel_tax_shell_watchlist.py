"""Monitor for flagged or suspicious entities."""

from __future__ import annotations

import scrapy


class IsraelTaxAuthorityShellCompanyWatchlistSpider(scrapy.Spider):
    """Monitor for flagged or suspicious entities."""

    name = "israeltaxauthorityshellcompanywatchlistspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
