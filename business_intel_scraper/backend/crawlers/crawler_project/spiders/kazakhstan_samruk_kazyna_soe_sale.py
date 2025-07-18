import scrapy


class KazakhstanSamrukKazynaSoeSaleSpider(scrapy.Spider):
    name = "kazakhstan_samruk_kazyna_soe_sale"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
