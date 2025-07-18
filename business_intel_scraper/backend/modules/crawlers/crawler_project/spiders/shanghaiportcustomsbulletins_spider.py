"""Spider for Shanghai Port Customs Bulletins (placeholder)."""

import scrapy


class ShanghaiPortCustomsBulletinsSpider(scrapy.Spider):
    """Placeholder spider for Shanghai Port Customs Bulletins."""

    name = "shanghaiportcustomsbulletins"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
