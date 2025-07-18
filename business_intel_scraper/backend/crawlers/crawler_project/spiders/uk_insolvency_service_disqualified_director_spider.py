from __future__ import annotations

import scrapy


class UkInsolvencyServiceDisqualifiedDirectorSpider(scrapy.Spider):
    """Placeholder for the UK Insolvency Service Disqualified Director."""

    name = "uk_insolvency_service_disqualified_director_spider"

    def parse(self, response: scrapy.http.Response):
        raise NotImplementedError("Spider not yet implemented")
