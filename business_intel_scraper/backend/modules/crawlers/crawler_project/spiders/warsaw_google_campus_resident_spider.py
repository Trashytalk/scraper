from __future__ import annotations

import scrapy


class WarsawGoogleCampusResidentSpider(scrapy.Spider):
    """Placeholder for the Warsaw Google Campus Resident."""

    name = "warsaw_google_campus_resident_spider"

    def parse(self, response: scrapy.http.Response):
        raise NotImplementedError("Spider not yet implemented")
