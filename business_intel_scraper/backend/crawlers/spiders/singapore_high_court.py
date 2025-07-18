"""Track commercial litigation and cross-border enforcement actions."""

from __future__ import annotations

import scrapy


class SingaporeHighCourtSpider(scrapy.Spider):
    """Track commercial litigation and cross-border enforcement actions."""

    name = "singaporehighcourtspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
