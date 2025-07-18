import scrapy


class UsCityHealthInspectionReportSpider(scrapy.Spider):
    name = "us_city_health_inspection_report"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
