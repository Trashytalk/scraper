import scrapy


class UaeDpWorldTerminalOperatorSpider(scrapy.Spider):
    name = "uae_dp_world_terminal_operator"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
