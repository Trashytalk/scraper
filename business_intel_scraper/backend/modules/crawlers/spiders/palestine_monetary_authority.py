"""Gather bank and corporate license data."""

from __future__ import annotations

import scrapy


class PalestineMonetaryAuthorityRegistrySpider(scrapy.Spider):
    """Gather bank and corporate license data."""

    name = "palestinemonetaryauthorityregistryspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
