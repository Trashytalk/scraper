"""Track trade permits issued by ministries."""

import scrapy


class TradePermitSpider(scrapy.Spider):
    """Track trade permits issued by ministries."""

    name = "tradepermitspider"
    allowed_domains = ["moc.gov.kh"]
    start_urls = ["https://www.moc.gov.kh"]

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"url": response.url}
