"""Spider gathering union and labor dispute information."""

from __future__ import annotations

import scrapy


class UnionLaborDisputeSpider(scrapy.Spider):
    """Collect rulings, actions, or strike data."""

    name = "union_labor_dispute"

    def parse(self, response: scrapy.http.Response):
        yield {}
