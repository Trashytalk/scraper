from __future__ import annotations

import scrapy


class MalaysiaYouthEntrepreneurAwardSpider(scrapy.Spider):
    """Placeholder for the Malaysia Youth Entrepreneur Award."""

    name = "malaysia_youth_entrepreneur_award_spider"

    def parse(self, response: scrapy.http.Response):
        raise NotImplementedError("Spider not yet implemented")
