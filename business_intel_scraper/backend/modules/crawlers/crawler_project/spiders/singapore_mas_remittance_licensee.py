import scrapy


class SingaporeMasRemittanceLicenseeSpider(scrapy.Spider):
    name = "singapore_mas_remittance_licensee"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
