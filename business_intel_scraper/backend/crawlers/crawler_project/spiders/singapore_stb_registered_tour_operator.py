import scrapy


class SingaporeStbRegisteredTourOperatorSpider(scrapy.Spider):
    name = "singapore_stb_registered_tour_operator"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
