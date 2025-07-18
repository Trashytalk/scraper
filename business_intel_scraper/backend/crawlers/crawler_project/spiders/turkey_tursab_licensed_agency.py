import scrapy


class TurkeyTursabLicensedAgencySpider(scrapy.Spider):
    name = "turkey_tursab_licensed_agency"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
