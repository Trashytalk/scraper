"""Spider scraping ultimate beneficial owner registries."""

from __future__ import annotations

import scrapy


class UBOSpider(scrapy.Spider):
    """Collect true beneficial ownership data."""

    name = "ubo"

    def parse(self, response: scrapy.http.Response):
        yield {}
