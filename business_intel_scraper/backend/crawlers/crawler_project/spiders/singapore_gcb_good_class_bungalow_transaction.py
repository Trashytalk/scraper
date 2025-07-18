import scrapy


class SingaporeGcbGoodClassBungalowTransactionSpider(scrapy.Spider):
    name = "singapore_gcb_good_class_bungalow_transaction"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
