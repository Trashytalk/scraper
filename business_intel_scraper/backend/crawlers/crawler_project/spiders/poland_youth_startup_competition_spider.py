from __future__ import annotations

import scrapy


class PolandYouthStartupCompetitionSpider(scrapy.Spider):
    """Placeholder for the Poland Youth Startup Competition."""

    name = "poland_youth_startup_competition_spider"

    def parse(self, response: scrapy.http.Response):
        raise NotImplementedError("Spider not yet implemented")
