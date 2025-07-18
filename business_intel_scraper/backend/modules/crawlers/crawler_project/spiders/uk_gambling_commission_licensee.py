import scrapy


class UkGamblingCommissionLicenseeSpider(scrapy.Spider):
    name = "uk_gambling_commission_licensee"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
