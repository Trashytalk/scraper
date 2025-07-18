import scrapy


class PolandLuxuryRealEstateBuyerSpider(scrapy.Spider):
    name = "poland_luxury_real_estate_buyer"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
