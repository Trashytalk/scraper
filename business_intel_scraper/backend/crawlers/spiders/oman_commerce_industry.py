"""Monitor company registrations, amendments, and dissolved businesses."""

from __future__ import annotations

import scrapy


class OmanCommerceIndustryRegistrySpider(scrapy.Spider):
    """Monitor company registrations, amendments, and dissolved businesses."""

    name = "omancommerceindustryregistryspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
