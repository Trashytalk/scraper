import scrapy


class SingaporePsaContainerLineOwnerSpider(scrapy.Spider):
    name = "singapore_psa_container_line_owner"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
