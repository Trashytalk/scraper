from __future__ import annotations

import scrapy


class TurkeyTuvturkFleetRegistrySpider(scrapy.Spider):
    """Placeholder for the Turkey TUVTURK Fleet Registry."""

    name = "turkey_tuvturk_fleet_registry_spider"

    def parse(self, response: scrapy.http.Response):
        raise NotImplementedError("Spider not yet implemented")
