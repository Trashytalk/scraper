"""Map offshore company and trust structures unique to Labuan FSA."""

from __future__ import annotations

import scrapy


class MalaysiaLabuanRegistrySpider(scrapy.Spider):
    """Map offshore company and trust structures unique to Labuan FSA."""

    name = "malaysialabuanregistryspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
