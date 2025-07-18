import scrapy


class SingaporeCraCasinoLicenseRegistrySpider(scrapy.Spider):
    name = "singapore_cra_casino_license_registry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
