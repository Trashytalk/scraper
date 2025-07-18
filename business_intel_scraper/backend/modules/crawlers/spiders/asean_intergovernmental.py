"""Map companies interacting with or registered to ASEAN cross-border platforms."""

from __future__ import annotations

import scrapy


class AseanIntergovernmentalRegistrySpider(scrapy.Spider):
    """Map companies interacting with or registered to ASEAN cross-border platforms."""

    name = "aseanintergovernmentalregistryspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
