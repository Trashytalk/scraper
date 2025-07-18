"""Spider gathering payment processor partnerships."""

from __future__ import annotations

import scrapy


class PaymentProcessorSpider(scrapy.Spider):
    """Extract data on companies' financial partners."""

    name = "payment_processor"

    def parse(self, response: scrapy.http.Response):
        yield {}
