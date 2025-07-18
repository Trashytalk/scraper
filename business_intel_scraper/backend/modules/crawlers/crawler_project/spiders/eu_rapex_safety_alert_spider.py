from __future__ import annotations

import scrapy


class EuRapexSafetyAlertSpider(scrapy.Spider):
    """Placeholder for the EU RAPEX Safety Alert."""

    name = "eu_rapex_safety_alert_spider"

    def parse(self, response: scrapy.http.Response):
        raise NotImplementedError("Spider not yet implemented")
