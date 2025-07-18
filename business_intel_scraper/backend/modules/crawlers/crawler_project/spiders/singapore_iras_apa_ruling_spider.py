from __future__ import annotations

import scrapy


class SingaporeIrasApaRulingSpider(scrapy.Spider):
    """Placeholder for the Singapore IRAS APA Ruling."""

    name = "singapore_iras_apa_ruling_spider"

    def parse(self, response: scrapy.http.Response):
        raise NotImplementedError("Spider not yet implemented")
