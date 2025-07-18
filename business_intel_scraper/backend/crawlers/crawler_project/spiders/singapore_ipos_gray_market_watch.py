import scrapy


class SingaporeIposGrayMarketWatchSpider(scrapy.Spider):
    name = "singapore_ipos_gray_market_watch"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
