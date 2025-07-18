from __future__ import annotations

import scrapy


class CambodiaMfiBorrowerListSpider(scrapy.Spider):
    """Placeholder for the Cambodia MFI Borrower List."""

    name = "cambodia_mfi_borrower_list_spider"

    def parse(self, response: scrapy.http.Response):
        raise NotImplementedError("Spider not yet implemented")
