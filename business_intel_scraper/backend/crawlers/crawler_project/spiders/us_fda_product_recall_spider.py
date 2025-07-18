from __future__ import annotations

import scrapy


class UsFdaProductRecallSpider(scrapy.Spider):
    """Placeholder for the US FDA Product Recall."""

    name = "us_fda_product_recall_spider"

    def parse(self, response: scrapy.http.Response):
        raise NotImplementedError("Spider not yet implemented")
