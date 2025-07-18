from __future__ import annotations

import scrapy


class MalaysiaEdgeSmeRankingSpider(scrapy.Spider):
    """Placeholder for the Malaysia Edge SME Ranking."""

    name = "malaysia_edge_sme_ranking_spider"

    def parse(self, response: scrapy.http.Response):
        raise NotImplementedError("Spider not yet implemented")
