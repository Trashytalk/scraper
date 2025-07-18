"""Collect regional IP filings from the Gulf Cooperation Council Patent Office."""

from __future__ import annotations

import scrapy


class GCCPatentOfficeRegistrySpider(scrapy.Spider):
    """Collect regional IP filings from the Gulf Cooperation Council Patent Office."""

    name = "gccpatentofficeregistryspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
