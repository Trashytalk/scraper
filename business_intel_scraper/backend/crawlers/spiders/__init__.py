"""Placeholder spiders for future implementation."""
"""Regional Scrapy spider definitions."""
"""Collection of additional business intelligence spiders."""

from __future__ import annotations

from .business_registration_change import BusinessRegistrationChangeSpider
from .ubo import UBOSpider
from .shell_company import ShellCompanySpider
from .payment_processor import PaymentProcessorSpider
from .arbitration_dispute import ArbitrationDisputeSpider
from .export_license import ExportLicenseSpider
from .insurance_certificate import InsuranceCertificateSpider
from .commodity_trading import CommodityTradingSpider
from .ipo_event import IPOEventSpider
from .bonds_debt_issuance import BondsDebtIssuanceSpider
from .business_association import BusinessAssociationSpider
from .franchise_directory import FranchiseDirectorySpider
from .nonprofit_registry import NonprofitRegistrySpider
from .asset_auction import AssetAuctionSpider
from .procurement_blacklist import ProcurementBlacklistSpider
from .bank_regulator_enforcement import BankRegulatorEnforcementSpider
from .business_license_revocation import BusinessLicenseRevocationSpider
from .foreign_investment_review import ForeignInvestmentReviewSpider
from .aml_fine import AMLFineSpider
from .cross_border_payment import CrossBorderPaymentSpider
from .e_invoicing import EInvoicingSpider
from .government_lobbying_spend import GovernmentLobbyingSpendSpider
from .whistleblower_report import WhistleblowerReportSpider
from .foreign_branch import ForeignBranchSpider
from .supplier_buyer import SupplierBuyerSpider
from .customs_port_call import CustomsPortCallSpider
from .competition_watchdog import CompetitionWatchdogSpider
from .pe_vc_portfolio import PEVCPortfolioSpider
from .union_labor_dispute import UnionLaborDisputeSpider
from .bankruptcy_asset_sale import BankruptcyAssetSaleSpider


__all__ = [
    "BusinessRegistrationChangeSpider",
    "UBOSpider",
    "ShellCompanySpider",
    "PaymentProcessorSpider",
    "ArbitrationDisputeSpider",
    "ExportLicenseSpider",
    "InsuranceCertificateSpider",
    "CommodityTradingSpider",
    "IPOEventSpider",
    "BondsDebtIssuanceSpider",
    "BusinessAssociationSpider",
    "FranchiseDirectorySpider",
    "NonprofitRegistrySpider",
    "AssetAuctionSpider",
    "ProcurementBlacklistSpider",
    "BankRegulatorEnforcementSpider",
    "BusinessLicenseRevocationSpider",
    "ForeignInvestmentReviewSpider",
    "AMLFineSpider",
    "CrossBorderPaymentSpider",
    "EInvoicingSpider",
    "GovernmentLobbyingSpendSpider",
    "WhistleblowerReportSpider",
    "ForeignBranchSpider",
    "SupplierBuyerSpider",
    "CustomsPortCallSpider",
    "CompetitionWatchdogSpider",
    "PEVCPortfolioSpider",
    "UnionLaborDisputeSpider",
    "BankruptcyAssetSaleSpider",
]
