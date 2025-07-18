import scrapy


class UaeAdgmSpvCompanyListSpider(scrapy.Spider):
    name = "uae_adgm_spv_company_list"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
