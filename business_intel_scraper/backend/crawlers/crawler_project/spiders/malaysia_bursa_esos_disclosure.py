import scrapy


class MalaysiaBursaEsosDisclosureSpider(scrapy.Spider):
    name = "malaysia_bursa_esos_disclosure"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
