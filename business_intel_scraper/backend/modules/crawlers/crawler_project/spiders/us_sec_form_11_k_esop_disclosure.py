import scrapy


class UsSecForm11KEsopDisclosureSpider(scrapy.Spider):
    name = "us_sec_form_11_k_esop_disclosure"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
