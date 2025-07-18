import scrapy


class SingaporeMasSpvRegisterSpider(scrapy.Spider):
    name = "singapore_mas_spv_register"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
