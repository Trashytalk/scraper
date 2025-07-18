"""Monitor company formation and annual reporting."""

from __future__ import annotations

import scrapy


class SerbiaBusinessRegistersAgencySpider(scrapy.Spider):
    """Monitor company formation and annual reporting."""

    name = "serbiabusinessregistersagencyspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
