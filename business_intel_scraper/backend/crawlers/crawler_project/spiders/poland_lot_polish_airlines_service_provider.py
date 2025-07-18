import scrapy


class PolandLotPolishAirlinesServiceProviderSpider(scrapy.Spider):
    name = "poland_lot_polish_airlines_service_provider"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
