"""Spider monitoring international arbitration cases."""

from __future__ import annotations

import scrapy


class ArbitrationDisputeSpider(scrapy.Spider):
    """Track cross-border disputes or settlements."""

    name = "arbitration_dispute"

    def parse(self, response: scrapy.http.Response):
        yield {}
