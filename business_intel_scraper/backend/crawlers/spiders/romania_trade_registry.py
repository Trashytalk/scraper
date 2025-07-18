"""Monitor company creation, dissolution, and director changes."""

from __future__ import annotations

import scrapy


class RomaniaTradeRegistrySpider(scrapy.Spider):
    """Monitor company creation, dissolution, and director changes."""

    name = "romaniatraderegistryspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
