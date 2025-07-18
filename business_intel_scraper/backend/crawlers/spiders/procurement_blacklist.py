"""Spider scraping procurement blacklists."""

from __future__ import annotations

import scrapy


class ProcurementBlacklistSpider(scrapy.Spider):
    """Gather lists of banned suppliers or vendors."""

    name = "procurement_blacklist"

    def parse(self, response: scrapy.http.Response):
        yield {}
