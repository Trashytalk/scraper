from __future__ import annotations

import scrapy


class UsExImBankAwardPayoutSpider(scrapy.Spider):
    """Placeholder for the US Ex-Im Bank Award Payout."""

    name = "us_ex_im_bank_award_payout_spider"

    def parse(self, response: scrapy.http.Response):
        raise NotImplementedError("Spider not yet implemented")
