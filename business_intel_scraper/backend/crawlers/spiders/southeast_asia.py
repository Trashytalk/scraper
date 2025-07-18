import scrapy


class SingaporeStraitsTimesMalaysianStarCorporateNewsSpider(scrapy.Spider):
    """Scrape corporate news from Singapore Straits Times and Malaysian Star."""

    name = "singapore_straits_times_malaysian_star_corporate_news"
    allowed_domains = ["straitstimes.com", "thestar.com.my"]
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse corporate news listings."""
        raise NotImplementedError


class SingaporeMASEnforcementActionsSpider(scrapy.Spider):
    """Gather enforcement actions from the Monetary Authority of Singapore."""

    name = "singapore_mas_enforcement_actions"
    allowed_domains = ["mas.gov.sg"]
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse MAS enforcement actions."""
        raise NotImplementedError


class ThailandBoardOfInvestmentSpider(scrapy.Spider):
    """Track incentives and approvals from Thailand's BOI."""

    name = "thailand_board_of_investment"
    allowed_domains = ["boi.go.th"]
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse BOI project approvals."""
        raise NotImplementedError


class VietnamExportProcessingZoneRegistrySpider(scrapy.Spider):
    """Monitor company listings in Vietnam export processing zones."""

    name = "vietnam_export_processing_zone_registry"
    allowed_domains = [".vn"]
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse export processing zone registry."""
        raise NotImplementedError


class IndonesiaOJKEnforcementSpider(scrapy.Spider):
    """Collect enforcement actions from Indonesia's OJK."""

    name = "indonesia_ojk_enforcement"
    allowed_domains = ["ojk.go.id"]
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse OJK enforcement announcements."""
        raise NotImplementedError


class MalaysiaSCDisclosureSpider(scrapy.Spider):
    """Scrape disclosure updates from Malaysia's Securities Commission."""

    name = "malaysia_sc_disclosure"
    allowed_domains = ["sc.com.my"]
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse SC disclosures."""
        raise NotImplementedError


class CambodiaMinistryOfCommerceFilingsSpider(scrapy.Spider):
    """Harvest company filings from Cambodia's Ministry of Commerce."""

    name = "cambodia_moc_filings"
    allowed_domains = ["moc.gov.kh"]
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse MoC company filings."""
        raise NotImplementedError


class AseanPepCorruptionCaseSpider(scrapy.Spider):
    """Aggregate ASEAN media sources for PEP and corruption cases."""

    name = "asean_pep_corruption_case"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse corruption case references."""
        raise NotImplementedError


class RegionalTaxTribunalJudgmentSpider(scrapy.Spider):
    """Scrape regional tax tribunal judgments in Southeast Asia."""

    name = "regional_tax_tribunal_judgment"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse tax tribunal decisions."""
        raise NotImplementedError


class SeAsiaRenewableEnergyCarbonCreditRegistrySpider(scrapy.Spider):
    """Gather data on renewable energy and carbon credit registries."""

    name = "se_asia_renewable_energy_carbon_credit_registry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse registry entries."""
        raise NotImplementedError


class PhilippinesPhilgepsProcurementSpider(scrapy.Spider):
    """Scrape the Philippine Government Electronic Procurement System."""

    name = "philippines_philgeps_procurement"
    allowed_domains = ["philgeps.gov.ph"]
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse procurement notices."""
        raise NotImplementedError


class VietnamStateSecuritiesCommissionPenaltySpider(scrapy.Spider):
    """Monitor penalties from Vietnam's State Securities Commission."""

    name = "vietnam_ssc_penalty"
    allowed_domains = ["ssc.gov.vn"]
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse SSC penalty announcements."""
        raise NotImplementedError
