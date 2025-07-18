"""Harvest business registration, sector, and membership data."""

from __future__ import annotations

import scrapy


class KuwaitChamberCommerceSpider(scrapy.Spider):
    """Harvest business registration, sector, and membership data."""

    name = "kuwaitchambercommercespider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
