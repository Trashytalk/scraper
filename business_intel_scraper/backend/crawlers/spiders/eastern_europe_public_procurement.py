"""Scrape public procurement portals in Eastern Europe.

Gather awardees, blacklists, and contract information from national and local
portals.
"""

from __future__ import annotations

import scrapy


class EasternEuropeRegionalPublicProcurementSpider(scrapy.Spider):
    """Scrape procurement portals for contracts and sanctions."""

    name = "easterneuroperegionalpublicprocurementspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
