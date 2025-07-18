"""Track companies, directors, and regulatory filings in Myanmar's DICA portal."""

from __future__ import annotations

import scrapy


class MyanmarDICASpider(scrapy.Spider):
    """Track companies, directors, and regulatory filings in Myanmar's DICA portal."""

    name = "myanmardicaspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
