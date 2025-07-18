from __future__ import annotations

import scrapy


class TurkeyBddkSuspiciousBankAccountClosureSpider(scrapy.Spider):
    """Placeholder for the Turkey BDDK Suspicious Bank Account Closure."""

    name = "turkey_bddk_suspicious_bank_account_closure_spider"

    def parse(self, response: scrapy.http.Response):
        raise NotImplementedError("Spider not yet implemented")
