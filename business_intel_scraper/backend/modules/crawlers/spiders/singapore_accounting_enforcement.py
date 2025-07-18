"""Monitor accounting and auditing enforcement in Singapore.

Track regulatory actions, license revocations, and other measures against
accounting or audit firms.
"""

from __future__ import annotations

import scrapy


class SingaporeAccountingEnforcementSpider(scrapy.Spider):
    """Spider for accounting enforcement actions."""

    name = "singaporeaccountingenforcementspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
