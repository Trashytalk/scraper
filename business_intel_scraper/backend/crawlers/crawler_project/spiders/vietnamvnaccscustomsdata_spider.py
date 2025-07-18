"""Spider for Vietnam VNACCS Customs Data (placeholder)."""

import scrapy


class VietnamVnaccsCustomsDataSpider(scrapy.Spider):
    """Placeholder spider for Vietnam VNACCS Customs Data."""

    name = "vietnamvnaccscustomsdata"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
