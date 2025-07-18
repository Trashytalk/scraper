"""Track company ownership and sanction compliance in Belarus."""

from __future__ import annotations

import scrapy


class BelarusUnifiedStateRegisterSpider(scrapy.Spider):
    """Track company ownership and sanction compliance in Belarus."""

    name = "belarusunifiedstateregisterspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
