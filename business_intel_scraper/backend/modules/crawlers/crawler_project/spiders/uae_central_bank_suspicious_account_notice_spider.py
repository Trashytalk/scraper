from __future__ import annotations

import scrapy


class UaeCentralBankSuspiciousAccountNoticeSpider(scrapy.Spider):
    """Placeholder for the UAE Central Bank Suspicious Account Notice."""

    name = "uae_central_bank_suspicious_account_notice_spider"

    def parse(self, response: scrapy.http.Response):
        raise NotImplementedError("Spider not yet implemented")
