import scrapy


class SingaporeMasCryptoExchangeLicenseeSpider(scrapy.Spider):
    name = "singapore_mas_crypto_exchange_licensee"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
