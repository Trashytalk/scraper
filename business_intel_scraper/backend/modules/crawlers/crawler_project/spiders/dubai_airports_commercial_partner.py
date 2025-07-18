import scrapy


class DubaiAirportsCommercialPartnerSpider(scrapy.Spider):
    name = "dubai_airports_commercial_partner"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
