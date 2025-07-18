"""Track registered companies and trade licenses."""

from __future__ import annotations

import scrapy


class IraqTradeDirectorySpider(scrapy.Spider):
    """Track registered companies and trade licenses."""

    name = "iraqtradedirectoryspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
