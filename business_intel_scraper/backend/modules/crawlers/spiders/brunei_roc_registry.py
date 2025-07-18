"""Monitor company filings from Brunei's registry.

Track changes from the Registry of Companies and Business Names.
"""

from __future__ import annotations

import scrapy


class BruneiRocRegistrySpider(scrapy.Spider):
    """Monitor filings and changes from the ROC registry."""

    name = "bruneirocregistryspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
