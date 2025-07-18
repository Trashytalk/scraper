import scrapy


class SecuritiesRegulatorFilingsSpider(scrapy.Spider):
    """Spider stub for Securities regulator filings (global)."""

    name = "securities_regulator_filings"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class BankruptcyInsolvencyProceedingListsSpider(scrapy.Spider):
    """Spider stub for Bankruptcy/insolvency proceeding lists."""

    name = "bankruptcy_insolvency_proceeding_lists"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class CompanyAnnualReportFinancialStatementSpider(scrapy.Spider):
    """Spider stub for Company annual report/financial statement spider."""

    name = "company_annual_report_financial_statement_spider"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class CrossListedStockExchangeDataSpider(scrapy.Spider):
    """Spider stub for Cross-listed stock exchange data spider."""

    name = "cross_listed_stock_exchange_data_spider"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class ShareholderRegistrySpider(scrapy.Spider):
    """Spider stub for Shareholder registry spider (when public)."""

    name = "shareholder_registry_spider"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class MutualFundEtfHoldingsSpidersSpider(scrapy.Spider):
    """Spider stub for Mutual fund/ETF holdings spiders."""

    name = "mutual_fund_etf_holdings_spiders"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class ForeignDirectInvestmentFilingsSpider(scrapy.Spider):
    """Spider stub for Foreign direct investment filings."""

    name = "foreign_direct_investment_filings"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class ForeignAgentRegistrationSpider(scrapy.Spider):
    """Spider stub for Foreign agent registration (e.g., US FARA, UK, Australia)."""

    name = "foreign_agent_registration"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class LobbyingRegistryFilingsSpider(scrapy.Spider):
    """Spider stub for Lobbying registry filings
    (non-US, e.g., EU, Canada, Australia)."""

    name = "lobbying_registry_filings"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class PoliticalRiskInsuranceRegistriesSpider(scrapy.Spider):
    """Spider stub for Political risk insurance registries."""

    name = "political_risk_insurance_registries"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class AmlCftEnforcementActionListsSpider(scrapy.Spider):
    """Spider stub for AML/CFT enforcement action lists."""

    name = "aml_cft_enforcement_action_lists"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class SanctionsPepWatchlistsSpider(scrapy.Spider):
    """Spider stub for Sanctions/PEP watchlists (country/UN/regional/global)."""

    name = "sanctions_pep_watchlists"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class AmlAuditReportsSummarySpider(scrapy.Spider):
    """Spider stub for AML audit reports/summary spider."""

    name = "aml_audit_reports_summary_spider"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class TaxBlacklistGreylistSpider(scrapy.Spider):
    """Spider stub for Tax blacklist/greylist spider (OECD, EU, national)."""

    name = "tax_blacklist_greylist_spider"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class TaxHavenLowTaxJurisdictionCompanyListingsSpider(scrapy.Spider):
    """Spider stub for Tax haven/low-tax jurisdiction company listings."""

    name = "tax_haven_low_tax_jurisdiction_company_listings"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class VatGstRegistrySpider(scrapy.Spider):
    """Spider stub for VAT/GST registry (EU, LATAM, APAC)."""

    name = "vat_gst_registry"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class TransferPricingRulingDisclosureSpider(scrapy.Spider):
    """Spider stub for Transfer pricing ruling disclosure spider."""

    name = "transfer_pricing_ruling_disclosure_spider"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class TaxDisputeLitigationRegistrySpider(scrapy.Spider):
    """Spider stub for Tax dispute/litigation registry."""

    name = "tax_dispute_litigation_registry"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class FinancialRegulatoryWarningInvestorAlertListsSpider(scrapy.Spider):
    """Spider stub for Financial regulatory warning/investor alert lists."""

    name = "financial_regulatory_warning_investor_alert_lists"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class InsiderTradingConvictionListsSpider(scrapy.Spider):
    """Spider stub for Insider trading conviction lists."""

    name = "insider_trading_conviction_lists"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class MoneyLaunderingConvictionCourtBulletinsSpider(scrapy.Spider):
    """Spider stub for Money laundering conviction court bulletins."""

    name = "money_laundering_conviction_court_bulletins"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class FraudConvictionListsSpider(scrapy.Spider):
    """Spider stub for Fraud conviction lists (all available countries)."""

    name = "fraud_conviction_lists"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class AntitrustCompetitionAuthorityCasesSpider(scrapy.Spider):
    """Spider stub for Antitrust/competition authority cases."""

    name = "antitrust_competition_authority_cases"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class CustomsFraudOrSmugglingConvictionListsSpider(scrapy.Spider):
    """Spider stub for Customs fraud or smuggling conviction lists."""

    name = "customs_fraud_or_smuggling_conviction_lists"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class AssetForfeitureAssetFreezeRegistriesSpider(scrapy.Spider):
    """Spider stub for Asset forfeiture/asset freeze registries."""

    name = "asset_forfeiture_asset_freeze_registries"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class EnvironmentalViolationFinesSpider(scrapy.Spider):
    """Spider stub for Environmental violation fines."""

    name = "environmental_violation_fines"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class ExportControlViolationListsSpider(scrapy.Spider):
    """Spider stub for Export control violation lists."""

    name = "export_control_violation_lists"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class ProcurementFraudBlacklistSpider(scrapy.Spider):
    """Spider stub for Procurement fraud blacklist spider."""

    name = "procurement_fraud_blacklist_spider"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class LaborLawViolationPenaltyRegistersSpider(scrapy.Spider):
    """Spider stub for Labor law violation/penalty registers."""

    name = "labor_law_violation_penalty_registers"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class OccupationalLicensingBoardSanctionsSpider(scrapy.Spider):
    """Spider stub for Occupational licensing board sanctions."""

    name = "occupational_licensing_board_sanctions"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class QualityAssuranceIsoAuditReportRegistrySpider(scrapy.Spider):
    """Spider stub for Quality assurance/ISO audit report registry."""

    name = "quality_assurance_iso_audit_report_registry"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class SafetyIncidentAccidentViolationDatabasesSpider(scrapy.Spider):
    """Spider stub for Safety incident/accident violation databases."""

    name = "safety_incident_accident_violation_databases"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class IntellectualPropertyLitigationRegistriesSpider(scrapy.Spider):
    """Spider stub for Intellectual property litigation registries."""

    name = "intellectual_property_litigation_registries"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class PatentTrademarkOppositionObjectionBulletinsSpider(scrapy.Spider):
    """Spider stub for Patent/trademark opposition/objection bulletins."""

    name = "patent_trademark_opposition_objection_bulletins"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class CopyrightRoyaltyTribunalFilingsSpider(scrapy.Spider):
    """Spider stub for Copyright royalty tribunal filings."""

    name = "copyright_royalty_tribunal_filings"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class DataPrivacyBreachNotificationListsSpider(scrapy.Spider):
    """Spider stub for Data privacy breach notification lists."""

    name = "data_privacy_breach_notification_lists"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class GdprCcpaPrivacyComplianceFilingsSpider(scrapy.Spider):
    """Spider stub for GDPR/CCPA privacy compliance filings."""

    name = "gdpr_ccpa_privacy_compliance_filings"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class DigitalPlatformComplianceReportingSpider(scrapy.Spider):
    """Spider stub for Digital platform compliance reporting spider."""

    name = "digital_platform_compliance_reporting_spider"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class RegulatorPublishedWhistleblowerRewardListsSpider(scrapy.Spider):
    """Spider stub for Regulator-published whistleblower reward lists."""

    name = "regulator_published_whistleblower_reward_lists"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class RegulatorySandboxInnovationLicenseeListsSpider(scrapy.Spider):
    """Spider stub for Regulatory sandbox/innovation licensee lists."""

    name = "regulatory_sandbox_innovation_licensee_lists"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class CommodityFuturesRegulatoryActionReportsSpider(scrapy.Spider):
    """Spider stub for Commodity futures regulatory action reports."""

    name = "commodity_futures_regulatory_action_reports"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class FinancialProductMisSellingListsSpider(scrapy.Spider):
    """Spider stub for Financial product mis-selling lists."""

    name = "financial_product_mis_selling_lists"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class CorporateBondDefaultAndRestructuringListsSpider(scrapy.Spider):
    """Spider stub for Corporate bond default and restructuring lists."""

    name = "corporate_bond_default_and_restructuring_lists"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class NonPerformingLoanSaleRegistriesSpider(scrapy.Spider):
    """Spider stub for Non-performing loan sale registries."""

    name = "non_performing_loan_sale_registries"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class RealEstateAuctionForeclosureListingsSpider(scrapy.Spider):
    """Spider stub for Real estate auction/foreclosure listings."""

    name = "real_estate_auction_foreclosure_listings"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class BankSavingsCooperativeFailureAndMergerDataSpider(scrapy.Spider):
    """Spider stub for Bank/savings cooperative failure and merger data."""

    name = "bank_savings_cooperative_failure_and_merger_data"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class CharityNgoComplianceOrFineRegistriesSpider(scrapy.Spider):
    """Spider stub for Charity/NGO compliance or fine registries."""

    name = "charity_ngo_compliance_or_fine_registries"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class PoliticalContributionCampaignFinanceFilingsSpider(scrapy.Spider):
    """Spider stub for Political contribution/campaign finance filings."""

    name = "political_contribution_campaign_finance_filings"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class ForeignExchangeLicenseeListingsSpider(scrapy.Spider):
    """Spider stub for Foreign exchange licensee listings."""

    name = "foreign_exchange_licensee_listings"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError


class ExportImportComplianceWarningListsSpider(scrapy.Spider):
    """Spider stub for Export-import compliance warning lists."""

    name = "export_import_compliance_warning_lists"

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        raise NotImplementedError
