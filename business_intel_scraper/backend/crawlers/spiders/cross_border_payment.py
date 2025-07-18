"""Spider for cross-border payment data."""

from __future__ import annotations

import scrapy


class CrossBorderPaymentSpider(scrapy.Spider):
    """Scrape payment traffic or flagged transactions."""

    name = "cross_border_payment"

    def parse(self, response: scrapy.http.Response):
        yield {}
