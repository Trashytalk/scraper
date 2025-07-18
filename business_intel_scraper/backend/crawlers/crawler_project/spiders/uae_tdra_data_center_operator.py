import scrapy


class UaeTdraDataCenterOperatorSpider(scrapy.Spider):
    name = "uae_tdra_data_center_operator"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
