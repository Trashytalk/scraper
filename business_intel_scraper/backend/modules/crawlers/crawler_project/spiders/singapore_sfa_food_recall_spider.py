from __future__ import annotations

import scrapy


class SingaporeSfaFoodRecallSpider(scrapy.Spider):
    """Placeholder for the Singapore SFA Food Recall."""

    name = "singapore_sfa_food_recall_spider"

    def parse(self, response: scrapy.http.Response):
        raise NotImplementedError("Spider not yet implemented")
