import scrapy


class PolandLocalMunicipalMarketPermitSpider(scrapy.Spider):
    name = "poland_local_municipal_market_permit"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
