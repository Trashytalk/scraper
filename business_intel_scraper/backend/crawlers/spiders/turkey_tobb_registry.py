"""Track chamber-registered businesses and affiliated organizations."""

from __future__ import annotations

import scrapy


class TurkeyTOBBRegistrySpider(scrapy.Spider):
    """Track chamber-registered businesses and affiliated organizations."""

    name = "turkeytobbregistryspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
