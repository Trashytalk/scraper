import scrapy


class PolandEnergyRegulatoryOfficeConsumptionDataSpider(scrapy.Spider):
    name = "poland_energy_regulatory_office_consumption_data"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
