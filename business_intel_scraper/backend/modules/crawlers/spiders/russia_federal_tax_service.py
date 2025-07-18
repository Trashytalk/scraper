"""Monitor Russian company/entrepreneur filings and updates."""

from __future__ import annotations

import scrapy


class RussiaFederalTaxServiceRegistrySpider(scrapy.Spider):
    """Monitor Russian company/entrepreneur filings and updates."""

    name = "russiafederaltaxserviceregistryspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
