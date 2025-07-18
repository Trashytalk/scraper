from __future__ import annotations

import scrapy


class UkHmTreasuryPppProjectSpider(scrapy.Spider):
    """Placeholder for the UK HM Treasury PPP Project."""

    name = "uk_hm_treasury_ppp_project_spider"

    def parse(self, response: scrapy.http.Response):
        raise NotImplementedError("Spider not yet implemented")
