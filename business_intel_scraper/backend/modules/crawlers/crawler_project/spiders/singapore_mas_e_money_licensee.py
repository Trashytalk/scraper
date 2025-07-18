import scrapy


class SingaporeMasEMoneyLicenseeSpider(scrapy.Spider):
    name = "singapore_mas_e_money_licensee"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
