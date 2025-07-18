import scrapy


class PolandUkeCloudServicesRegistrySpider(scrapy.Spider):
    name = "poland_uke_cloud_services_registry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
