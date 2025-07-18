import scrapy


class TurkeyBddkMobilePaymentLicenseeSpider(scrapy.Spider):
    name = "turkey_bddk_mobile_payment_licensee"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
