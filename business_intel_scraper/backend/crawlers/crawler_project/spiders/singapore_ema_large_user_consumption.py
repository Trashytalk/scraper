import scrapy


class SingaporeEmaLargeUserConsumptionSpider(scrapy.Spider):
    name = "singapore_ema_large_user_consumption"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
