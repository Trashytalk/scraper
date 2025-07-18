import scrapy


class UsCbpGrayMarketSeizureSpider(scrapy.Spider):
    name = "us_cbp_gray_market_seizure"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
