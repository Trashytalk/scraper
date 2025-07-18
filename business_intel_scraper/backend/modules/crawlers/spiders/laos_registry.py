"""Scrape Laos company registration and annual report databases."""

from __future__ import annotations

import scrapy


class LaosRegistrySpider(scrapy.Spider):
    """Scrape Laos company registration and annual report databases."""

    name = "laosregistryspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
