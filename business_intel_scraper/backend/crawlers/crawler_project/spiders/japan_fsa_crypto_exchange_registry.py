import scrapy


class JapanFsaCryptoExchangeRegistrySpider(scrapy.Spider):
    name = "japan_fsa_crypto_exchange_registry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
