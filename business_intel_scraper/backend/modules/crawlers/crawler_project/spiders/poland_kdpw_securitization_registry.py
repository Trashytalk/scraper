import scrapy


class PolandKdpwSecuritizationRegistrySpider(scrapy.Spider):
    name = "poland_kdpw_securitization_registry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
