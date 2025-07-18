"""Spider for FATF High risk Jurisdictions Country List (placeholder)."""

import scrapy


class FatfHighRiskJurisdictionsCountryListSpider(scrapy.Spider):
    """Placeholder spider for FATF High risk Jurisdictions Country List."""

    name = "fatfhighriskjurisdictionscountrylist"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
