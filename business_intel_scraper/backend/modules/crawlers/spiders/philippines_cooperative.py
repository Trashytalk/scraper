"""Harvest records of registered business cooperatives."""

from __future__ import annotations

import scrapy


class PhilippinesCooperativeDevelopmentAuthoritySpider(scrapy.Spider):
    """Harvest records of registered business cooperatives."""

    name = "philippinescooperativedevelopmentauthorityspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
