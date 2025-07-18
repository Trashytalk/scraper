import scrapy


class PolandGpwGreenBondRegistrySpider(scrapy.Spider):
    name = "poland_gpw_green_bond_registry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
