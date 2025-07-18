"""Spider for NYSE/Nasdaq EDGAR 10-K 20-F (placeholder)."""

import scrapy


class NyseNasdaqEdgar10K20FSpider(scrapy.Spider):
    """Placeholder spider for NYSE/Nasdaq EDGAR 10-K 20-F."""

    name = "nysenasdaqedgar10k20f"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
