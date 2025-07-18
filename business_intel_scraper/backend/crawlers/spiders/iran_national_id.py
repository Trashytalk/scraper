"""Scrape Iran's national ID registry.

Harvest business identification and tax compliance lists when available.
"""

from __future__ import annotations

import scrapy


class IranNationalIdRegistrySpider(scrapy.Spider):
    """Collect national ID and tax compliance data."""

    name = "irannationalidregistryspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
