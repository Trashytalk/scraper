"""Scrape the Cambodia real estate registry.

Gather property developers and project approvals from the Ministry of Land
Management.
"""

from __future__ import annotations

import scrapy


class CambodiaRealEstateRegistrySpider(scrapy.Spider):
    """Scrape property developers and project approvals."""

    name = "cambodiarealestateregistryspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
