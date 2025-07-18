"""Spider monitoring IPO or funding events."""

from __future__ import annotations

import scrapy


class IPOEventSpider(scrapy.Spider):
    """Monitor market sources for IPO registrations."""

    name = "ipo_event"

    def parse(self, response: scrapy.http.Response):
        yield {}
