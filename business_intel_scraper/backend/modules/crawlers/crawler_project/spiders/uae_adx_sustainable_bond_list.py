import scrapy


class UaeAdxSustainableBondListSpider(scrapy.Spider):
    name = "uae_adx_sustainable_bond_list"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
