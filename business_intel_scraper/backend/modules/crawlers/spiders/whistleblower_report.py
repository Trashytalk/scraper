"""Spider monitoring whistleblower or complaint portals."""

from __future__ import annotations

import scrapy


class WhistleblowerReportSpider(scrapy.Spider):
    """Harvest early risk signals from reports."""

    name = "whistleblower_report"

    def parse(self, response: scrapy.http.Response):
        yield {}
