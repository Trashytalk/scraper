"""
Template Manager for Business Intelligence Extraction

This module manages extraction templates and configurations for different types
of business content.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Union
from enum import Enum
import json
import re


class TemplateType(Enum):
    COMPANY_PROFILE = "company_profile"
    CONTACT_INFO = "contact_info"
    FINANCIAL_DATA = "financial_data"
    NEWS_ARTICLE = "news_article"
    PRODUCT_INFO = "product_info"
    EXECUTIVE_BIO = "executive_bio"
    REGULATORY_FILING = "regulatory_filing"


@dataclass
class ExtractionRule:
    """Defines a single extraction rule"""
    name: str
    selector: str  # CSS selector or XPath
    attribute: Optional[str] = None  # HTML attribute to extract
    regex: Optional[str] = None  # Post-processing regex
    required: bool = True
    default_value: Any = None


@dataclass
class ExtractionTemplate:
    """Extraction template for a specific content type"""
    template_id: str
    name: str
    template_type: TemplateType
    rules: List[ExtractionRule]
    confidence_threshold: float = 0.6
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class TemplateManager:
    """Manages extraction templates and applies them to content"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.templates: Dict[str, ExtractionTemplate] = {}
        self._load_default_templates()
    
    def _load_default_templates(self):
        """Load default extraction templates"""
        
        # Company Profile Template
        company_profile_rules = [
            ExtractionRule("company_name", "h1, .company-name, [class*='company']", required=True),
            ExtractionRule("description", "meta[name='description']", "content"),
            ExtractionRule("industry", ".industry, [class*='industry']"),
            ExtractionRule("founded", ".founded, [class*='founded']"),
            ExtractionRule("headquarters", ".headquarters, [class*='location']"),
            ExtractionRule("employees", ".employees, [class*='employee']"),
            ExtractionRule("revenue", ".revenue, [class*='revenue']"),
        ]
        
        self.templates["company_profile"] = ExtractionTemplate(
            template_id="company_profile",
            name="Company Profile",
            template_type=TemplateType.COMPANY_PROFILE,
            rules=company_profile_rules,
            metadata={"priority": "high", "category": "business_info"}
        )
        
        # Contact Information Template
        contact_rules = [
            ExtractionRule("email", "a[href^='mailto:']", "href", r"mailto:(.+)"),
            ExtractionRule("phone", "a[href^='tel:']", "href", r"tel:(.+)"),
            ExtractionRule("address", ".address, [class*='address']"),
            ExtractionRule("postal_code", ".postal, [class*='zip']"),
            ExtractionRule("website", "a[href^='http']", "href"),
        ]
        
        self.templates["contact_info"] = ExtractionTemplate(
            template_id="contact_info", 
            name="Contact Information",
            template_type=TemplateType.CONTACT_INFO,
            rules=contact_rules,
            metadata={"priority": "medium", "category": "contact"}
        )
        
        # Financial Data Template
        financial_rules = [
            ExtractionRule("stock_symbol", ".ticker, [class*='symbol']"),
            ExtractionRule("market_cap", ".market-cap, [class*='market']"),
            ExtractionRule("share_price", ".price, [class*='share']"),
            ExtractionRule("pe_ratio", ".pe-ratio, [class*='pe']"),
            ExtractionRule("dividend_yield", ".dividend, [class*='yield']"),
        ]
        
        self.templates["financial_data"] = ExtractionTemplate(
            template_id="financial_data",
            name="Financial Data", 
            template_type=TemplateType.FINANCIAL_DATA,
            rules=financial_rules,
            metadata={"priority": "high", "category": "financials"}
        )
    
    def get_template(self, template_id: str) -> Optional[ExtractionTemplate]:
        """Get template by ID"""
        return self.templates.get(template_id)
    
    def get_templates_by_type(self, template_type: TemplateType) -> List[ExtractionTemplate]:
        """Get all templates of a specific type"""
        return [t for t in self.templates.values() if t.template_type == template_type]
    
    def add_template(self, template: ExtractionTemplate) -> bool:
        """Add a new template"""
        try:
            self.templates[template.template_id] = template
            return True
        except Exception:
            return False
    
    def apply_template(self, template_id: str, content: str, url: str = "") -> Dict[str, Any]:
        """Apply extraction template to content"""
        template = self.get_template(template_id)
        if not template:
            return {}
        
        try:
            # Try to use lxml for better parsing
            from lxml import html
            doc = html.fromstring(content)
            use_lxml = True
        except ImportError:
            # Fallback to basic regex extraction
            use_lxml = False
            doc = content
        
        extracted_data = {}
        confidence_scores = {}
        
        for rule in template.rules:
            try:
                if use_lxml:
                    value = self._extract_with_lxml(doc, rule)
                else:
                    value = self._extract_with_regex(content, rule)
                
                if value:
                    extracted_data[rule.name] = value
                    confidence_scores[rule.name] = 0.8
                elif rule.default_value:
                    extracted_data[rule.name] = rule.default_value
                    confidence_scores[rule.name] = 0.3
                elif rule.required:
                    confidence_scores[rule.name] = 0.0
                
            except Exception as e:
                if rule.required:
                    confidence_scores[rule.name] = 0.0
                continue
        
        # Calculate overall confidence
        if confidence_scores:
            avg_confidence = sum(confidence_scores.values()) / len(confidence_scores)
        else:
            avg_confidence = 0.0
        
        return {
            "data": extracted_data,
            "confidence": avg_confidence,
            "template_id": template_id,
            "url": url,
            "field_confidences": confidence_scores
        }
    
    def _extract_with_lxml(self, doc, rule: ExtractionRule) -> Optional[str]:
        """Extract using lxml"""
        try:
            elements = doc.cssselect(rule.selector)
            if not elements:
                return None
            
            element = elements[0]
            
            if rule.attribute:
                value = element.get(rule.attribute, "").strip()
            else:
                value = element.text_content().strip()
            
            if rule.regex and value:
                match = re.search(rule.regex, value)
                if match:
                    value = match.group(1) if match.groups() else match.group(0)
            
            return value if value else None
            
        except Exception:
            return None
    
    def _extract_with_regex(self, content: str, rule: ExtractionRule) -> Optional[str]:
        """Fallback extraction using regex patterns"""
        try:
            # Convert CSS selectors to rough regex patterns
            if rule.name == "email":
                pattern = r'mailto:([^"\'>\s]+)'
                match = re.search(pattern, content)
                return match.group(1) if match else None
            
            elif rule.name == "phone":
                pattern = r'tel:([^"\'>\s]+)'
                match = re.search(pattern, content)
                return match.group(1) if match else None
            
            elif rule.name == "company_name":
                # Look for title tag or h1 content
                pattern = r'<title[^>]*>([^<]+)</title>|<h1[^>]*>([^<]+)</h1>'
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    return (match.group(1) or match.group(2)).strip()
            
            elif rule.name == "description":
                pattern = r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']'
                match = re.search(pattern, content, re.IGNORECASE)
                return match.group(1) if match else None
            
            return None
            
        except Exception:
            return None
    
    def get_manager_stats(self) -> Dict[str, Any]:
        """Get template manager statistics"""
        template_types = {}
        for template in self.templates.values():
            template_type = template.template_type.value
            template_types[template_type] = template_types.get(template_type, 0) + 1
        
        return {
            "total_templates": len(self.templates),
            "template_types": template_types,
            "templates": {
                tid: {
                    "name": template.name,
                    "type": template.template_type.value,
                    "rules": len(template.rules),
                    "confidence_threshold": template.confidence_threshold
                }
                for tid, template in self.templates.items()
            }
        }
