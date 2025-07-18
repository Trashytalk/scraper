"""Spider mapping foreign branches and subsidiaries."""

from __future__ import annotations

import scrapy


class ForeignBranchSpider(scrapy.Spider):
    """Collect global footprint information."""

    name = "foreign_branch"

    def parse(self, response: scrapy.http.Response):
        yield {}
