from __future__ import annotations

import scrapy


class PolandEconomicForumExhibitorSpider(scrapy.Spider):
    """Placeholder for the Poland Economic Forum Exhibitor."""

    name = "poland_economic_forum_exhibitor_spider"

    def parse(self, response: scrapy.http.Response):
        raise NotImplementedError("Spider not yet implemented")
