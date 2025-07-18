"""Spider extracting data from e-invoicing platforms."""

from __future__ import annotations

import scrapy


class EInvoicingSpider(scrapy.Spider):
    """Harvest publicly disclosed invoices."""

    name = "e_invoicing"

    def parse(self, response: scrapy.http.Response):
        yield {}
