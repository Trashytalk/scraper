"""Example Scrapy spider."""

from __future__ import annotations

import scrapy

from ...security import solve_captcha

from ...proxy.provider import DummyProxyProvider
from .browser import BrowserCrawler


class ExampleSpider(scrapy.Spider):
    """Simple spider that scrapes example.com."""

    name = "example"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com"]

    # Configure proxy middleware and provider
    base = "business_intel_scraper.backend.modules.crawlers.middleware"
    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            f"{base}.ProxyMiddleware": 543,
            f"{base}.RandomUserAgentMiddleware": 544,
            f"{base}.RandomDelayMiddleware": 545,
        },
        "PROXY_PROVIDER": DummyProxyProvider(["http://localhost:8000"]),
    }

    def __init__(
        self,
        *args,
        use_browser: bool = False,
        headless: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.use_browser = use_browser
        self.headless = headless

    def start_requests(self):
        if self.use_browser:
            crawler = BrowserCrawler(headless=self.headless)
            for url in self.start_urls:
                html = crawler.fetch(url)
                response = scrapy.http.TextResponse(url=url, body=html.encode("utf-8"))
                yield self.parse(response)
        else:
            for url in self.start_urls:
                yield scrapy.Request(url, callback=self.parse)

    def parse(
        self,
        response: scrapy.http.Response,
    ) -> scrapy.Item | dict[str, str]:
        """Parse the response.

        Parameters
        ----------
        response : scrapy.http.Response
            The HTTP response to parse.

        Returns
        -------
        scrapy.Item | dict[str, str]
            Parsed item from the page.
        """
        if "captcha" in response.text.lower():
            solve_captcha(b"dummy")
            return {}

        return {"url": response.url}


class UtilityProcurementSpider(scrapy.Spider):
    """Scrape utility procurement registries for business changes."""

    name = "utility_procurement"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"source": response.url}


class OccupationalLicensingBoardSpider(scrapy.Spider):
    """Gather licenses for regulated professions."""

    name = "occupational_licensing_board"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"source": response.url}


class SmallBusinessSetAsideRegistrySpider(scrapy.Spider):
    """Monitor set-aside eligible supplier portals."""

    name = "small_business_set_aside_registry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"source": response.url}


class CorporateSocialMediaAdSpendSpider(scrapy.Spider):
    """Track ad spend from social media transparency portals."""

    name = "corporate_social_media_ad_spend"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"source": response.url}


class SupplierQualityComplianceCertificationSpider(scrapy.Spider):
    """Collect supplier quality and compliance certificates."""

    name = "supplier_quality_compliance_certification"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"source": response.url}


class GovernmentRebateTaxCreditSpider(scrapy.Spider):
    """Gather published lists of government incentive recipients."""

    name = "government_rebate_tax_credit"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"source": response.url}


class ForeignAgentRegistrationSpider(scrapy.Spider):
    """Monitor FARA and similar foreign agent registries."""

    name = "foreign_agent_registration"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"source": response.url}


class ImportExportLicenseRevocationSpider(scrapy.Spider):
    """Track revocations of import/export privileges."""

    name = "import_export_license_revocation"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"source": response.url}


class ShippingFlagRegistrySpider(scrapy.Spider):
    """Harvest ship or aircraft flag registry data."""

    name = "shipping_flag_registry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"source": response.url}


class FreightForwarderCustomsBrokerSpider(scrapy.Spider):
    """Scrape directories of freight forwarders and customs brokers."""

    name = "freight_forwarder_customs_broker"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"source": response.url}


class BusinessRestructuringSpinOffSpider(scrapy.Spider):
    """Track announced business spinoffs and restructurings."""

    name = "business_restructuring_spin_off"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"source": response.url}


class CrossBorderWorkforceVisaSponsorshipSpider(scrapy.Spider):
    """Gather data on company work visa sponsorships."""

    name = "cross_border_workforce_visa_sponsorship"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"source": response.url}


class CarbonCreditOffsetRegistrySpider(scrapy.Spider):
    """Scrape carbon credit and offset registries."""

    name = "carbon_credit_offset_registry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"source": response.url}


class PaymentDisputeChargebackSpider(scrapy.Spider):
    """Monitor portals for commercial payment disputes."""

    name = "payment_dispute_chargeback"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"source": response.url}


class IPOWithdrawalDelistingSpider(scrapy.Spider):
    """Track IPO withdrawals and exchange delistings."""

    name = "ipo_withdrawal_delisting"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"source": response.url}


class BusinessIntelligenceLeakSpider(scrapy.Spider):
    """Monitor archives for leaked business intelligence."""

    name = "business_intelligence_leak"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"source": response.url}


class InternationalStandardsBodyMembershipSpider(scrapy.Spider):
    """Track business participation in standards bodies."""

    name = "international_standards_body_membership"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"source": response.url}


class PublicUtilityShareholderSpider(scrapy.Spider):
    """Scrape regulatory filings for utility shareholders."""

    name = "public_utility_shareholder"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"source": response.url}


class GovernmentPermitApplicationSpider(scrapy.Spider):
    """Track new or pending business permit applications."""

    name = "government_permit_application"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"source": response.url}


class BusinessRelocationIncentiveSpider(scrapy.Spider):
    """Scrape incentives for business relocations or expansions."""

    name = "business_relocation_incentive"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"source": response.url}


class BusinessTelemetryIoTRegistrySpider(scrapy.Spider):
    """Monitor public IoT registries for company endpoints."""

    name = "business_telemetry_iot_registry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"source": response.url}


class DebtRecoveryCollectionsSpider(scrapy.Spider):
    """Gather businesses involved in debt recovery proceedings."""

    name = "debt_recovery_collections"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"source": response.url}


class IntellectualPropertyLitigationSpider(scrapy.Spider):
    """Monitor IP litigation cases for businesses."""

    name = "intellectual_property_litigation"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"source": response.url}


class ProcurementDiversitySpider(scrapy.Spider):
    """Harvest supplier diversity certification lists."""

    name = "procurement_diversity"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"source": response.url}


class CriticalInfrastructureRegistrySpider(scrapy.Spider):
    """Gather lists of businesses designated as critical infrastructure."""

    name = "critical_infrastructure_registry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"source": response.url}


class BusinessResilienceContinuityPlanningSpider(scrapy.Spider):
    """Scrape published business continuity plans."""

    name = "business_resilience_continuity_planning"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"source": response.url}


class InvestorRelationsPresentationSpider(scrapy.Spider):
    """Collect investor relations presentations and transcripts."""

    name = "investor_relations_presentation"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"source": response.url}


class CrossBorderDataTransferComplianceSpider(scrapy.Spider):
    """Gather self-certifications for cross-border data transfers."""

    name = "cross_border_data_transfer_compliance"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"source": response.url}


class BankingCorrespondentRelationshipSpider(scrapy.Spider):
    """Collect public data on correspondent banking relationships."""

    name = "banking_correspondent_relationship"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"source": response.url}


class SustainabilityESGReportSpider(scrapy.Spider):
    """Scrape sustainability and ESG disclosures."""

    name = "sustainability_esg_report"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"source": response.url}
