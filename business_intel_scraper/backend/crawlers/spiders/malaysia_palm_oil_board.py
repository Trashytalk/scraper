"""Track Malaysia's palm oil board registry.

Gather company registration, export license, and sustainability certification
records.
"""

from __future__ import annotations

import scrapy


class MalaysiaPalmOilBoardProducerRegistrySpider(scrapy.Spider):
    """Track palm oil company licensing and certification."""

    name = "malaysiapalmoilboardproducerregistryspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
