import scrapy


class TurkeyEkISZlKBusinessReviewSpider(scrapy.Spider):
    name = "turkey_ek_i_s_zl_k_business_review"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
