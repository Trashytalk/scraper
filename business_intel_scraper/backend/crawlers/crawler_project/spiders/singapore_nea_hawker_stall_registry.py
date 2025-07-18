import scrapy


class SingaporeNeaHawkerStallRegistrySpider(scrapy.Spider):
    name = "singapore_nea_hawker_stall_registry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
