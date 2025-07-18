"""Monitor companies subject to import/export restrictions or blacklisting."""

from __future__ import annotations

import scrapy


class EgyptCustomsImportExportBlacklistSpider(scrapy.Spider):
    """Monitor companies subject to import/export restrictions or blacklisting."""

    name = "egyptcustomsimportexportblacklistspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
