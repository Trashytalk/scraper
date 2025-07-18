"""Monitor filings, bankruptcy, and director changes."""

from __future__ import annotations

import scrapy


class BulgariaCommercialRegisterSpider(scrapy.Spider):
    """Monitor filings, bankruptcy, and director changes."""

    name = "bulgariacommercialregisterspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
