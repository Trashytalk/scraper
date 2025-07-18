"""Spider monitoring competition regulator announcements."""

from __future__ import annotations

import scrapy


class CompetitionWatchdogSpider(scrapy.Spider):
    """Scrape anti-trust violation or merger cases."""

    name = "competition_watchdog"

    def parse(self, response: scrapy.http.Response):
        yield {}
