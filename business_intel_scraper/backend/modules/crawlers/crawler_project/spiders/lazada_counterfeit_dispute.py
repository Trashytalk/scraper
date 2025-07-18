import scrapy


class LazadaCounterfeitDisputeSpider(scrapy.Spider):
    name = "lazada_counterfeit_dispute"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
