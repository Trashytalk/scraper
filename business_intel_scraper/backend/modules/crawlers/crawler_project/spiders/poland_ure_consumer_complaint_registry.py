import scrapy


class PolandUreConsumerComplaintRegistrySpider(scrapy.Spider):
    name = "poland_ure_consumer_complaint_registry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
