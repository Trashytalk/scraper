"""Monitor procurement portals in the Middle East."""

import scrapy


class MiddleEastProcurementSpider(scrapy.Spider):
    """Monitor procurement portals in the Middle East."""

    name = "middleeastprocurementspider"
    allowed_domains = ["etimad.sa"]
    start_urls = ["https://etimad.sa"]

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"url": response.url}
