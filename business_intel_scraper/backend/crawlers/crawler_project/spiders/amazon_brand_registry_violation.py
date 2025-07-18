import scrapy


class AmazonBrandRegistryViolationSpider(scrapy.Spider):
    name = "amazon_brand_registry_violation"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
