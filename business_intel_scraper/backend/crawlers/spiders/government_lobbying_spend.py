"""Spider collecting government lobbying expenditures."""

from __future__ import annotations

import scrapy


class GovernmentLobbyingSpendSpider(scrapy.Spider):
    """Collect actual monetary lobbying spend data."""

    name = "government_lobbying_spend"

    def parse(self, response: scrapy.http.Response):
        yield {}
