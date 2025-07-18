from __future__ import annotations

import scrapy


class StripePaymentPartnerDirectorySpider(scrapy.Spider):
    """Placeholder for the Stripe Payment Partner Directory."""

    name = "stripe_payment_partner_directory_spider"

    def parse(self, response: scrapy.http.Response):
        raise NotImplementedError("Spider not yet implemented")
