"""Spider collecting nonprofit or foundation registry data."""

from __future__ import annotations

import scrapy


class NonprofitRegistrySpider(scrapy.Spider):
    """Gather data on nonprofit foundations and links."""

    name = "nonprofit_registry"

    def parse(self, response: scrapy.http.Response):
        yield {}
