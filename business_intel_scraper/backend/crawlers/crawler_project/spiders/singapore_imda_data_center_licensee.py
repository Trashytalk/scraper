import scrapy


class SingaporeImdaDataCenterLicenseeSpider(scrapy.Spider):
    name = "singapore_imda_data_center_licensee"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
