"""Scrape company, shareholder, and license data."""

from __future__ import annotations

import scrapy


class BahrainCIORegistrySpider(scrapy.Spider):
    """Scrape company, shareholder, and license data."""

    name = "bahraincioregistryspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
