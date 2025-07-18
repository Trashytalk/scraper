"""Harvest filings from SE Asia IP offices."""

import scrapy


class SEAsiaPatentTrademarkSpider(scrapy.Spider):
    """Harvest filings from SE Asia IP offices."""

    name = "seasiapatenttrademarkspider"
    allowed_domains = ["ipos.gov.sg"]
    start_urls = ["https://www.ipos.gov.sg"]

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"url": response.url}
