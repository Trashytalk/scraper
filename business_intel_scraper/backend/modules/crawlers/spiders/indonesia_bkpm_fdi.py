"""Track major foreign investment approvals and project launches."""

from __future__ import annotations

import scrapy


class IndonesiaBkpmFdiSpider(scrapy.Spider):
    """Track major foreign investment approvals and project launches."""

    name = "indonesiabkpmfdispider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
