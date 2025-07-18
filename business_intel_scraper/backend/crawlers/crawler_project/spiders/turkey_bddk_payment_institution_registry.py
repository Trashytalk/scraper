import scrapy


class TurkeyBddkPaymentInstitutionRegistrySpider(scrapy.Spider):
    name = "turkey_bddk_payment_institution_registry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
