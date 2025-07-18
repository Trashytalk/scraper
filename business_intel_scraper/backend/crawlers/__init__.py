"""Crawler module providing Scrapy spiders and browser-based crawlers."""

try:
    from .spider import ExampleSpider
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    ExampleSpider = None  # type: ignore

from .browser import BrowserCrawler
from .playwright_utils import fetch_with_playwright
from .spiders.southeast_asia import (
    AseanPepCorruptionCaseSpider,
    CambodiaMinistryOfCommerceFilingsSpider,
    IndonesiaOJKEnforcementSpider,
    MalaysiaSCDisclosureSpider,
    PhilippinesPhilgepsProcurementSpider,
    RegionalTaxTribunalJudgmentSpider,
    SeAsiaRenewableEnergyCarbonCreditRegistrySpider,
    SingaporeMASEnforcementActionsSpider,
    SingaporeStraitsTimesMalaysianStarCorporateNewsSpider,
    ThailandBoardOfInvestmentSpider,
    VietnamExportProcessingZoneRegistrySpider,
    VietnamStateSecuritiesCommissionPenaltySpider,
)
from .spiders.middle_east import (
    AbuDhabiDubaiFreeZoneCompanyListSpider,
    DubaiCourtsLitigationAnnouncementSpider,
    DubaiLandDepartmentTitleDeedSpider,
    EgyptPublicBusinessSectorCompanyReportsSpider,
    GCCTaxAuthoritySpider,
    GCCTenderBlacklistAnnouncementsSpider,
    IranChamberOfCommerceMembershipSpider,
    IsraelInnovationAuthorityGrantsSpider,
    JordanCompaniesControlDepartmentRegistrySpider,
    KuwaitSaudiPublicProcurementSpider,
    QatarCentralBankAMLEnforcementSpider,
    SaudiNitaqatComplianceSpider,
    TurkeyKAPPublicDisclosurePlatformSpider,
)

__all__ = ["BrowserCrawler", "fetch_with_playwright"]
if ExampleSpider is not None:
    __all__.insert(0, "ExampleSpider")

__all__ += [
    "SingaporeStraitsTimesMalaysianStarCorporateNewsSpider",
    "SingaporeMASEnforcementActionsSpider",
    "ThailandBoardOfInvestmentSpider",
    "VietnamExportProcessingZoneRegistrySpider",
    "IndonesiaOJKEnforcementSpider",
    "MalaysiaSCDisclosureSpider",
    "CambodiaMinistryOfCommerceFilingsSpider",
    "AseanPepCorruptionCaseSpider",
    "RegionalTaxTribunalJudgmentSpider",
    "SeAsiaRenewableEnergyCarbonCreditRegistrySpider",
    "PhilippinesPhilgepsProcurementSpider",
    "VietnamStateSecuritiesCommissionPenaltySpider",
    "DubaiLandDepartmentTitleDeedSpider",
    "GCCTaxAuthoritySpider",
    "AbuDhabiDubaiFreeZoneCompanyListSpider",
    "KuwaitSaudiPublicProcurementSpider",
    "JordanCompaniesControlDepartmentRegistrySpider",
    "QatarCentralBankAMLEnforcementSpider",
    "IsraelInnovationAuthorityGrantsSpider",
    "IranChamberOfCommerceMembershipSpider",
    "EgyptPublicBusinessSectorCompanyReportsSpider",
    "SaudiNitaqatComplianceSpider",
    "GCCTenderBlacklistAnnouncementsSpider",
    "TurkeyKAPPublicDisclosurePlatformSpider",
    "DubaiCourtsLitigationAnnouncementSpider",
]
