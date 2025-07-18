import scrapy


class UaeMunicipalitySouqLicenseHolderSpider(scrapy.Spider):
    name = "uae_municipality_souq_license_holder"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
