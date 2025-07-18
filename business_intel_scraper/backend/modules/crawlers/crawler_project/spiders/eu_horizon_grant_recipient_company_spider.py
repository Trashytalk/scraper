from __future__ import annotations

import scrapy


class EuHorizonGrantRecipientCompanySpider(scrapy.Spider):
    """Placeholder for the EU Horizon Grant Recipient Company."""

    name = "eu_horizon_grant_recipient_company_spider"

    def parse(self, response: scrapy.http.Response):
        raise NotImplementedError("Spider not yet implemented")
