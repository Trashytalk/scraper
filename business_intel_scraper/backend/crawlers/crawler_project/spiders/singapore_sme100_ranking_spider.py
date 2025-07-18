from __future__ import annotations

import scrapy


class SingaporeSme100RankingSpider(scrapy.Spider):
    """Placeholder for the Singapore SME100 Ranking."""

    name = "singapore_sme100_ranking_spider"

    def parse(self, response: scrapy.http.Response):
        raise NotImplementedError("Spider not yet implemented")
