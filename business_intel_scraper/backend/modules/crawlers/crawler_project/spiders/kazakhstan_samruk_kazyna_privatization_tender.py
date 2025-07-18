import scrapy


class KazakhstanSamrukKazynaPrivatizationTenderSpider(scrapy.Spider):
    name = "kazakhstan_samruk_kazyna_privatization_tender"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
