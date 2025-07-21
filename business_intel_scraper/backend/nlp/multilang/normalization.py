"""
Multi-Language Field Normalization Module

Provides normalization and standardization for business entity fields
across different languages and formats.
"""

from __future__ import annotations

import re
import logging
from typing import List, Dict, Any, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime
import json
from decimal import Decimal, InvalidOperation

from .core import LanguageInfo, ScriptType, DetectedText, language_detector
from .transliteration import entity_normalizer

logger = logging.getLogger(__name__)


@dataclass
class NormalizedField:
    """Normalized field with original and standardized values"""
    original: str
    normalized: str
    field_type: str
    confidence: float
    language: LanguageInfo
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AddressComponents:
    """Structured address components"""
    street_number: Optional[str] = None
    street_name: Optional[str] = None
    building: Optional[str] = None
    floor: Optional[str] = None
    unit: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None
    state_province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    po_box: Optional[str] = None
    raw_components: List[str] = field(default_factory=list)


class PhoneNumberNormalizer:
    """Normalize phone numbers across different formats"""
    
    def __init__(self):
        # Country calling codes
        self.country_codes = {
            'US': '1', 'CA': '1', 'RU': '7', 'KZ': '7', 'CN': '86',
            'IN': '91', 'JP': '81', 'DE': '49', 'FR': '33', 'GB': '44',
            'IT': '39', 'ES': '34', 'BR': '55', 'MX': '52', 'AR': '54',
            'AU': '61', 'KR': '82', 'TH': '66', 'SA': '966', 'AE': '971',
            'EG': '20', 'ZA': '27', 'NG': '234', 'TR': '90', 'GR': '30'
        }
        
        # Reverse lookup
        self.code_to_country = {v: k for k, v in self.country_codes.items()}
    
    def normalize_phone(self, phone: str, default_country: str = 'US') -> NormalizedField:
        """Normalize phone number to E.164 format"""
        if not phone:
            return NormalizedField('', '', 'phone', 0.0, language_detector.language_data['en'])
        
        original = phone
        
        # Remove all non-digits except + at the start
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # Remove leading zeros after country code
        cleaned = re.sub(r'^(\+\d{1,3})0+', r'\1', cleaned)
        
        confidence = 0.5
        metadata = {}
        
        # Already has country code
        if cleaned.startswith('+'):
            if len(cleaned) >= 10:  # Minimum reasonable length
                normalized = cleaned
                confidence = 0.9
                
                # Extract country from code
                for length in [4, 3, 2, 1]:
                    country_code = cleaned[1:1+length]
                    if country_code in self.code_to_country:
                        metadata['country'] = self.code_to_country[country_code]
                        metadata['country_code'] = country_code
                        break
            else:
                normalized = cleaned
                confidence = 0.3
        
        # Add default country code
        elif len(cleaned) >= 7:  # Domestic number
            country_code = self.country_codes.get(default_country, '1')
            normalized = f"+{country_code}{cleaned}"
            confidence = 0.7
            metadata['country'] = default_country
            metadata['country_code'] = country_code
        
        else:
            # Too short to be valid
            normalized = cleaned
            confidence = 0.1
        
        # Validate final format
        if normalized.startswith('+') and len(normalized) >= 10:
            confidence = min(confidence + 0.1, 1.0)
        
        return NormalizedField(
            original, normalized, 'phone', confidence,
            language_detector.language_data['en'], metadata
        )


class AddressNormalizer:
    """Normalize addresses across different countries and languages"""
    
    def __init__(self):
        self.address_patterns = self._load_address_patterns()
        self.country_formats = self._load_country_formats()
    
    def _load_address_patterns(self) -> Dict[str, Dict[str, str]]:
        """Load address parsing patterns"""
        return {
            'street_number': {
                'en': r'^\d+[a-zA-Z]?(?:\s*[-/]\s*\d+[a-zA-Z]?)?',
                'zh': r'^\d+号',
                'ja': r'^\d+番地?',
                'ru': r'^\d+(?:\s*корпус\s*\d+)?'
            },
            'floor': {
                'en': r'(?:floor|fl\.?|level|lv\.?)\s*(\d+)',
                'zh': r'(\d+)楼',
                'ja': r'(\d+)階',
                'ru': r'(\d+)\s*этаж'
            },
            'unit': {
                'en': r'(?:unit|apt\.?|apartment|suite|ste\.?)\s*([a-zA-Z0-9]+)',
                'zh': r'(\d+)室',
                'ja': r'(\d+)号室',
                'ru': r'квартира\s*(\d+)'
            },
            'po_box': {
                'en': r'(?:P\.?O\.?\s*Box|Post\s*Office\s*Box)\s*(\d+)',
                'zh': r'邮政信箱\s*(\d+)',
                'ja': r'私書箱\s*(\d+)',
                'ru': r'а/я\s*(\d+)'
            }
        }
    
    def _load_country_formats(self) -> Dict[str, Dict[str, str]]:
        """Load country-specific address formats"""
        return {
            'US': {
                'format': '{street_number} {street_name}, {city}, {state} {postal_code}',
                'postal_code_pattern': r'\d{5}(?:-\d{4})?'
            },
            'CA': {
                'format': '{street_number} {street_name}, {city}, {state} {postal_code}',
                'postal_code_pattern': r'[A-Za-z]\d[A-Za-z]\s*\d[A-Za-z]\d'
            },
            'CN': {
                'format': '{state}{city}{district}{street_name}{street_number}号',
                'postal_code_pattern': r'\d{6}'
            },
            'JP': {
                'format': '〒{postal_code} {state}{city}{street_name}{street_number}',
                'postal_code_pattern': r'\d{3}-\d{4}'
            },
            'RU': {
                'format': '{postal_code}, {state}, {city}, {street_name}, {street_number}',
                'postal_code_pattern': r'\d{6}'
            },
            'DE': {
                'format': '{street_name} {street_number}, {postal_code} {city}',
                'postal_code_pattern': r'\d{5}'
            },
            'FR': {
                'format': '{street_number} {street_name}, {postal_code} {city}',
                'postal_code_pattern': r'\d{5}'
            }
        }
    
    def parse_address(self, address: str, language: LanguageInfo, 
                     country: Optional[str] = None) -> AddressComponents:
        """Parse address into structured components"""
        if not address:
            return AddressComponents()
        
        components = AddressComponents()
        components.raw_components = [comp.strip() for comp in address.split(',')]
        
        # Get patterns for the language
        patterns = {
            field_type: patterns.get(language.code, patterns.get('en', ''))
            for field_type, patterns in self.address_patterns.items()
        }
        
        # Extract street number
        if patterns['street_number']:
            match = re.search(patterns['street_number'], address, re.IGNORECASE)
            if match:
                components.street_number = match.group(0).strip()
        
        # Extract floor
        if patterns['floor']:
            match = re.search(patterns['floor'], address, re.IGNORECASE)
            if match:
                components.floor = match.group(1)
        
        # Extract unit/apartment
        if patterns['unit']:
            match = re.search(patterns['unit'], address, re.IGNORECASE)
            if match:
                components.unit = match.group(1)
        
        # Extract PO Box
        if patterns['po_box']:
            match = re.search(patterns['po_box'], address, re.IGNORECASE)
            if match:
                components.po_box = match.group(1)
        
        # Extract postal code if country format is known
        if country and country in self.country_formats:
            postal_pattern = self.country_formats[country]['postal_code_pattern']
            match = re.search(postal_pattern, address)
            if match:
                components.postal_code = match.group(0)
        
        return components
    
    def normalize_address(self, address: str, language: LanguageInfo, 
                         country: Optional[str] = None) -> NormalizedField:
        """Normalize address format"""
        if not address:
            return NormalizedField('', '', 'address', 0.0, language)
        
        components = self.parse_address(address, language, country)
        
        # Basic normalization
        normalized = address.strip()
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Standardize separators
        normalized = re.sub(r'[,;]\s*', ', ', normalized)
        
        confidence = 0.7
        metadata = {
            'components': components.__dict__,
            'country': country
        }
        
        return NormalizedField(
            address, normalized, 'address', confidence, language, metadata
        )


class CompanyIdentifierNormalizer:
    """Normalize company registration numbers and identifiers"""
    
    def __init__(self):
        self.id_patterns = self._load_id_patterns()
    
    def _load_id_patterns(self) -> Dict[str, Dict[str, str]]:
        """Load company ID patterns by country"""
        return {
            'US': {
                'EIN': r'\d{2}-\d{7}',
                'DUNS': r'\d{9}',
                'CIK': r'\d{10}'
            },
            'CN': {
                'USCC': r'[0-9A-Z]{18}',  # Unified Social Credit Code
                'ORG_CODE': r'[0-9A-Z]{8}-[0-9A-Z]'
            },
            'RU': {
                'INN': r'\d{10,12}',
                'OGRN': r'\d{13,15}',
                'KPP': r'\d{9}'
            },
            'IN': {
                'CIN': r'[UL]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6}',
                'PAN': r'[A-Z]{5}\d{4}[A-Z]'
            },
            'JP': {
                'CORPORATE_NUMBER': r'\d{13}'
            },
            'DE': {
                'HRB': r'HRB\s*\d+',
                'UST_ID': r'DE\d{9}'
            },
            'GB': {
                'COMPANY_NUMBER': r'\d{8}',
                'VAT': r'GB\d{9}'
            }
        }
    
    def normalize_company_id(self, identifier: str, country: Optional[str] = None, 
                           id_type: Optional[str] = None) -> NormalizedField:
        """Normalize company identifier"""
        if not identifier:
            return NormalizedField('', '', 'company_id', 0.0, language_detector.language_data['en'])
        
        original = identifier
        normalized = identifier.strip().upper()
        
        # Remove common separators and spaces
        cleaned = re.sub(r'[-\s.]', '', normalized)
        
        confidence = 0.5
        metadata = {}
        
        # If country and type are known, validate format
        if country and id_type and country in self.id_patterns:
            patterns = self.id_patterns[country]
            if id_type in patterns:
                pattern = patterns[id_type]
                if re.match(f'^{pattern}$', normalized):
                    confidence = 0.9
                    metadata['validated'] = True
                    metadata['format'] = id_type
        
        # Otherwise, try to identify format from patterns
        elif country and country in self.id_patterns:
            for format_name, pattern in self.id_patterns[country].items():
                if re.match(f'^{pattern}$', normalized):
                    confidence = 0.8
                    metadata['identified_format'] = format_name
                    metadata['country'] = country
                    break
        
        # Generic validation - check if it looks like a valid identifier
        if re.match(r'^[A-Z0-9\-]+$', normalized) and len(normalized) >= 5:
            confidence = max(confidence, 0.6)
        
        metadata['original'] = original
        metadata['cleaned'] = cleaned
        
        return NormalizedField(
            original, normalized, 'company_id', confidence,
            language_detector.language_data['en'], metadata
        )


class FinancialDataNormalizer:
    """Normalize financial amounts and currencies"""
    
    def __init__(self):
        # Currency codes and symbols
        self.currency_symbols = {
            '$': 'USD', '€': 'EUR', '£': 'GBP', '¥': 'JPY', '₽': 'RUB',
            '₹': 'INR', '¢': 'USD', '₩': 'KRW', '₡': 'CRC', '₪': 'ILS',
            '₦': 'NGN', '₨': 'PKR', '₱': 'PHP', '₹': 'INR', '₴': 'UAH'
        }
        
        self.currency_codes = [
            'USD', 'EUR', 'GBP', 'JPY', 'CNY', 'RUB', 'INR', 'KRW',
            'AUD', 'CAD', 'CHF', 'SEK', 'NOK', 'DKK', 'PLN', 'CZK',
            'HUF', 'BGN', 'RON', 'HRK', 'TRY', 'ILS', 'ZAR', 'BRL',
            'MXN', 'ARS', 'CLP', 'COP', 'PEN', 'UYU', 'SGD', 'HKD',
            'TWD', 'THB', 'MYR', 'IDR', 'PHP', 'VND', 'AED', 'SAR'
        ]
        
        # Number format patterns by locale
        self.number_formats = {
            'US': {'decimal': '.', 'thousand': ','},
            'EU': {'decimal': ',', 'thousand': '.'},
            'CH': {'decimal': '.', 'thousand': "'"},
            'IN': {'decimal': '.', 'thousand': ','}  # With lakh/crore
        }
    
    def normalize_amount(self, amount_str: str, default_currency: str = 'USD') -> NormalizedField:
        """Normalize financial amount"""
        if not amount_str:
            return NormalizedField('', '', 'amount', 0.0, language_detector.language_data['en'])
        
        original = amount_str
        amount_str = amount_str.strip()
        
        # Extract currency
        currency = None
        confidence = 0.5
        
        # Look for currency symbols
        for symbol, code in self.currency_symbols.items():
            if symbol in amount_str:
                currency = code
                amount_str = amount_str.replace(symbol, '').strip()
                confidence = 0.8
                break
        
        # Look for currency codes
        if not currency:
            for code in self.currency_codes:
                if re.search(rf'\b{code}\b', amount_str, re.IGNORECASE):
                    currency = code
                    amount_str = re.sub(rf'\b{code}\b', '', amount_str, flags=re.IGNORECASE).strip()
                    confidence = 0.7
                    break
        
        if not currency:
            currency = default_currency
            confidence = 0.5
        
        # Clean the number
        # Remove words like "million", "billion", etc.
        multiplier = 1
        multiplier_words = {
            'k': 1000, 'thousand': 1000,
            'm': 1000000, 'million': 1000000, 'mil': 1000000,
            'b': 1000000000, 'billion': 1000000000, 'bil': 1000000000,
            'lakh': 100000, 'crore': 10000000
        }
        
        for word, mult in multiplier_words.items():
            if re.search(rf'\b{word}\b', amount_str, re.IGNORECASE):
                multiplier = mult
                amount_str = re.sub(rf'\b{word}\b', '', amount_str, flags=re.IGNORECASE)
                confidence = min(confidence + 0.1, 1.0)
                break
        
        # Remove parentheses (negative amounts)
        negative = False
        if '(' in amount_str and ')' in amount_str:
            negative = True
            amount_str = re.sub(r'[()]', '', amount_str)
        
        # Extract numeric value
        # Handle different decimal/thousand separators
        amount_str = re.sub(r'[^\d.,]', '', amount_str)
        
        if not amount_str:
            return NormalizedField(original, original, 'amount', 0.0, language_detector.language_data['en'])
        
        # Determine decimal separator
        if ',' in amount_str and '.' in amount_str:
            # Both present - the last one is likely decimal
            if amount_str.rindex(',') > amount_str.rindex('.'):
                # Comma is decimal separator
                amount_str = amount_str.replace('.', '').replace(',', '.')
            else:
                # Period is decimal separator
                amount_str = amount_str.replace(',', '')
        elif ',' in amount_str:
            # Only comma - could be thousands or decimal
            comma_parts = amount_str.split(',')
            if len(comma_parts[-1]) <= 2:  # Likely decimal
                amount_str = amount_str.replace(',', '.')
            else:  # Likely thousands
                amount_str = amount_str.replace(',', '')
        
        # Convert to decimal
        try:
            numeric_value = Decimal(amount_str) * multiplier
            if negative:
                numeric_value = -numeric_value
            
            # Format normalized amount
            normalized = f"{currency} {numeric_value:.2f}"
            confidence = min(confidence + 0.2, 1.0)
            
        except (InvalidOperation, ValueError):
            normalized = original
            confidence = 0.1
        
        metadata = {
            'currency': currency,
            'numeric_value': str(numeric_value) if 'numeric_value' in locals() else None,
            'multiplier': multiplier,
            'negative': negative
        }
        
        return NormalizedField(
            original, normalized, 'amount', confidence,
            language_detector.language_data['en'], metadata
        )


class DateNormalizer:
    """Normalize dates across different formats and languages"""
    
    def __init__(self):
        self.month_names = {
            'en': ['january', 'february', 'march', 'april', 'may', 'june',
                   'july', 'august', 'september', 'october', 'november', 'december'],
            'zh': ['一月', '二月', '三月', '四月', '五月', '六月',
                   '七月', '八月', '九月', '十月', '十一月', '十二月'],
            'ja': ['1月', '2月', '3月', '4月', '5月', '6月',
                   '7月', '8月', '9月', '10月', '11月', '12月'],
            'ru': ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь',
                   'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь']
        }
        
        self.date_patterns = [
            r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY-MM-DD
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # MM/DD/YYYY or DD/MM/YYYY
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{2})',  # MM/DD/YY or DD/MM/YY
            r'(\d{4})年(\d{1,2})月(\d{1,2})日',      # Chinese format
            r'(\d{4})年(\d{1,2})月',                 # Chinese year-month
            r'(\d{1,2})\s+([a-zA-Zа-яё]+)\s+(\d{4})'  # DD Month YYYY
        ]
    
    def normalize_date(self, date_str: str, language: LanguageInfo) -> NormalizedField:
        """Normalize date to ISO format"""
        if not date_str:
            return NormalizedField('', '', 'date', 0.0, language)
        
        original = date_str
        confidence = 0.5
        metadata = {}
        
        # Try different patterns
        for pattern in self.date_patterns:
            match = re.search(pattern, date_str)
            if match:
                groups = match.groups()
                
                if '年' in pattern:  # Chinese format
                    year, month = groups[0], groups[1]
                    day = groups[2] if len(groups) > 2 else '01'
                    normalized = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    confidence = 0.9
                
                elif len(groups) == 3 and groups[0].isdigit() and groups[2].isdigit():
                    # Check if first group is year (4 digits)
                    if len(groups[0]) == 4:
                        year, month, day = groups[0], groups[1], groups[2]
                    elif len(groups[2]) == 4:
                        # MM/DD/YYYY or DD/MM/YYYY
                        year = groups[2]
                        # Ambiguous - assume MM/DD for US, DD/MM for others
                        if language.code == 'en':
                            month, day = groups[0], groups[1]
                        else:
                            day, month = groups[0], groups[1]
                        metadata['format_ambiguous'] = True
                    else:
                        # Two-digit year
                        year = '20' + groups[2] if int(groups[2]) < 50 else '19' + groups[2]
                        if language.code == 'en':
                            month, day = groups[0], groups[1]
                        else:
                            day, month = groups[0], groups[1]
                    
                    try:
                        normalized = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                        # Validate date
                        datetime.strptime(normalized, '%Y-%m-%d')
                        confidence = 0.8
                    except ValueError:
                        continue
                
                else:
                    # Month name format
                    continue
                
                metadata['pattern'] = pattern
                break
        else:
            # No pattern matched
            normalized = date_str
            confidence = 0.3
        
        return NormalizedField(
            original, normalized, 'date', confidence, language, metadata
        )


# Global instances
phone_normalizer = PhoneNumberNormalizer()
address_normalizer = AddressNormalizer()
company_id_normalizer = CompanyIdentifierNormalizer()
financial_normalizer = FinancialDataNormalizer()
date_normalizer = DateNormalizer()
