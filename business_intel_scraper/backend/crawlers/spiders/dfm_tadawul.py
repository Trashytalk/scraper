"""Scrape listings from DFM and Tadawul."""

import scrapy


class DFMTadawulListingSpider(scrapy.Spider):
    """Scrape listings from DFM and Tadawul."""

    name = "dfmtadawullistingspider"
    allowed_domains = ["dfm.ae"]
    start_urls = ["https://www.dfm.ae"]

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"url": response.url}
