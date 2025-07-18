from __future__ import annotations

import scrapy


class UsOccPublicEnforcementActionSpider(scrapy.Spider):
    """Placeholder for the US OCC Public Enforcement Action."""

    name = "us_occ_public_enforcement_action_spider"

    def parse(self, response: scrapy.http.Response):
        raise NotImplementedError("Spider not yet implemented")
