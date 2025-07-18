from __future__ import annotations

import scrapy


class SingaporeNrfResearchGrantWinnerSpider(scrapy.Spider):
    """Placeholder for the Singapore NRF Research Grant Winner."""

    name = "singapore_nrf_research_grant_winner_spider"

    def parse(self, response: scrapy.http.Response):
        raise NotImplementedError("Spider not yet implemented")
