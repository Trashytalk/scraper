import scrapy


class PolandKnfCryptoExchangeListSpider(scrapy.Spider):
    name = "poland_knf_crypto_exchange_list"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
