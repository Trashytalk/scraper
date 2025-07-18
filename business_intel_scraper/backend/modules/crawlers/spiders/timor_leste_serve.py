"""Collect company formation and licensing records."""

from __future__ import annotations

import scrapy


class TimorLesteServeRegistrySpider(scrapy.Spider):
    """Collect company formation and licensing records."""

    name = "timorlesteserveregistryspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
