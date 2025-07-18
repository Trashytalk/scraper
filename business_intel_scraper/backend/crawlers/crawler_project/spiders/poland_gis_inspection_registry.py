import scrapy


class PolandGisInspectionRegistrySpider(scrapy.Spider):
    name = "poland_gis_inspection_registry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
