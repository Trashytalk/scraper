from __future__ import annotations

import scrapy


class SingaporeEcgcRecipientSpider(scrapy.Spider):
    """Placeholder for the Singapore ECGC Recipient."""

    name = "singapore_ecgc_recipient_spider"

    def parse(self, response: scrapy.http.Response):
        raise NotImplementedError("Spider not yet implemented")
