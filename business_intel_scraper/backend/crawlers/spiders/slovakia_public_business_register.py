"""Track director, shareholder, and legal proceedings."""

from __future__ import annotations

import scrapy


class SlovakiaPublicBusinessRegisterSpider(scrapy.Spider):
    """Track director, shareholder, and legal proceedings."""

    name = "slovakiapublicbusinessregisterspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
