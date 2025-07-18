"""Scrape ownership, directors, and litigation data from the USR."""

from __future__ import annotations

import scrapy


class UkraineUnifiedStateRegisterSpider(scrapy.Spider):
    """Scrape ownership, directors, and litigation data from the USR."""

    name = "ukraineunifiedstateregisterspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
