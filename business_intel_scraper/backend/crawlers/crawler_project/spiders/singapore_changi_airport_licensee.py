import scrapy


class SingaporeChangiAirportLicenseeSpider(scrapy.Spider):
    name = "singapore_changi_airport_licensee"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
