from __future__ import annotations

import scrapy


class SingaporeEcgcPayoutRegistrySpider(scrapy.Spider):
    """Placeholder for the Singapore ECGC Payout Registry."""

    name = "singapore_ecgc_payout_registry_spider"

    def parse(self, response: scrapy.http.Response):
        raise NotImplementedError("Spider not yet implemented")
