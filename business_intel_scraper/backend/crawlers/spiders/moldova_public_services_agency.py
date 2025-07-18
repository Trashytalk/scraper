"""Harvest business registration and compliance data."""

from __future__ import annotations

import scrapy


class MoldovaPublicServicesAgencyRegistrySpider(scrapy.Spider):
    """Harvest business registration and compliance data."""

    name = "moldovapublicservicesagencyregistryspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
