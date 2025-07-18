"""Spider extracting customs records or port call data."""

from __future__ import annotations

import scrapy


class CustomsPortCallSpider(scrapy.Spider):
    """Connect companies with import/export activity."""

    name = "customs_port_call"

    def parse(self, response: scrapy.http.Response):
        yield {}
