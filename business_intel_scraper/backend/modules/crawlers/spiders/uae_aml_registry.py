"""Harvest enforcement actions against UAE companies for AML violations."""

from __future__ import annotations

import scrapy


class UAEAntiMoneyLaunderingActionRegistrySpider(scrapy.Spider):
    """Harvest enforcement actions against UAE companies for AML violations."""

    name = "uaeantimoneylaunderingactionregistryspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
