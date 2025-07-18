"""Harvest data from Turkey MERSIS and trade registry."""

import scrapy


class TurkeyMERSISRegistrySpider(scrapy.Spider):
    """Harvest data from Turkey MERSIS and trade registry."""

    name = "turkeymersisregistryspider"
    allowed_domains = ["mersis.gov.tr"]
    start_urls = ["https://mersis.gov.tr"]

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"url": response.url}
