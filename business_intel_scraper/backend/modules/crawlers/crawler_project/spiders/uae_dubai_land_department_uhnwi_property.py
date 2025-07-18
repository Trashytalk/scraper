import scrapy


class UaeDubaiLandDepartmentUhnwiPropertySpider(scrapy.Spider):
    name = "uae_dubai_land_department_uhnwi_property"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
