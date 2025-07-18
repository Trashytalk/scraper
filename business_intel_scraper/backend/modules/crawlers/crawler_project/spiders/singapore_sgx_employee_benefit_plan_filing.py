import scrapy


class SingaporeSgxEmployeeBenefitPlanFilingSpider(scrapy.Spider):
    name = "singapore_sgx_employee_benefit_plan_filing"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
