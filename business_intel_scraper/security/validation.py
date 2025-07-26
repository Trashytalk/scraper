"""
Input Validation and Sanitization
Comprehensive input validation, data sanitization, and schema validation
"""

import re
import json
import html
import bleach
import validators
from typing import Any, Dict, List, Optional, Union, Tuple, Type, get_type_hints
from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from enum import Enum
import ipaddress
from urllib.parse import urlparse
import base64
import unicodedata
import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Input validation error"""
    pass


class SanitizationError(Exception):
    """Input sanitization error"""
    pass


class DataType(Enum):
    """Supported data types for validation"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    EMAIL = "email"
    URL = "url"
    IP_ADDRESS = "ip_address"
    DATE = "date"
    DATETIME = "datetime"
    JSON = "json"
    BASE64 = "base64"
    UUID = "uuid"
    PHONE = "phone"
    CREDIT_CARD = "credit_card"
    POSTAL_CODE = "postal_code"
    ALPHANUMERIC = "alphanumeric"
    HTML = "html"
    SQL = "sql"
    REGEX = "regex"


@dataclass
class ValidationRule:
    """Validation rule configuration"""
    field_name: str
    data_type: DataType
    required: bool = True
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    pattern: Optional[str] = None
    allowed_values: Optional[List[Any]] = None
    custom_validator: Optional[callable] = None
    sanitize: bool = True
    sanitization_options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Validation result"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    sanitized_value: Any = None
    original_value: Any = None


class InputValidator:
    """Comprehensive input validation system"""
    
    # Common regex patterns
    PATTERNS = {
        'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'phone': r'^\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$',
        'uuid': r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$',
        'credit_card': r'^(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3[0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})$',
        'postal_code_us': r'^\d{5}(?:[-\s]\d{4})?$',
        'postal_code_ca': r'^[A-Za-z]\d[A-Za-z][ -]?\d[A-Za-z]\d$',
        'alphanumeric': r'^[a-zA-Z0-9]+$',
        'username': r'^[a-zA-Z0-9_.-]{3,20}$',
        'password_strong': r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
        'hex_color': r'^#(?:[0-9a-fA-F]{3}){1,2}$',
        'domain': r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    }
    
    @classmethod
    def validate_string(cls, value: Any, rule: ValidationRule) -> ValidationResult:
        """Validate string input"""
        result = ValidationResult(is_valid=True, original_value=value)
        
        # Convert to string
        if value is None:
            if rule.required:
                result.is_valid = False
                result.errors.append(f"{rule.field_name} is required")
                return result
            else:
                result.sanitized_value = ""
                return result
        
        str_value = str(value)
        result.sanitized_value = str_value
        
        # Length validation
        if rule.min_length is not None and len(str_value) < rule.min_length:
            result.is_valid = False
            result.errors.append(f"{rule.field_name} must be at least {rule.min_length} characters long")
        
        if rule.max_length is not None and len(str_value) > rule.max_length:
            result.is_valid = False
            result.errors.append(f"{rule.field_name} must not exceed {rule.max_length} characters")
        
        # Pattern validation
        if rule.pattern and not re.match(rule.pattern, str_value):
            result.is_valid = False
            result.errors.append(f"{rule.field_name} does not match required pattern")
        
        # Allowed values validation
        if rule.allowed_values and str_value not in rule.allowed_values:
            result.is_valid = False
            result.errors.append(f"{rule.field_name} must be one of: {', '.join(map(str, rule.allowed_values))}")
        
        # Custom validation
        if rule.custom_validator:
            try:
                custom_result = rule.custom_validator(str_value)
                if not custom_result:
                    result.is_valid = False
                    result.errors.append(f"{rule.field_name} failed custom validation")
            except Exception as e:
                result.is_valid = False
                result.errors.append(f"{rule.field_name} validation error: {str(e)}")
        
        return result
    
    @classmethod
    def validate_integer(cls, value: Any, rule: ValidationRule) -> ValidationResult:
        """Validate integer input"""
        result = ValidationResult(is_valid=True, original_value=value)
        
        if value is None:
            if rule.required:
                result.is_valid = False
                result.errors.append(f"{rule.field_name} is required")
                return result
            else:
                result.sanitized_value = 0
                return result
        
        try:
            if isinstance(value, str):
                # Remove whitespace and common formatting
                clean_value = value.strip().replace(',', '')
                int_value = int(clean_value)
            else:
                int_value = int(value)
            
            result.sanitized_value = int_value
            
            # Range validation
            if rule.min_value is not None and int_value < rule.min_value:
                result.is_valid = False
                result.errors.append(f"{rule.field_name} must be at least {rule.min_value}")
            
            if rule.max_value is not None and int_value > rule.max_value:
                result.is_valid = False
                result.errors.append(f"{rule.field_name} must not exceed {rule.max_value}")
            
            # Allowed values validation
            if rule.allowed_values and int_value not in rule.allowed_values:
                result.is_valid = False
                result.errors.append(f"{rule.field_name} must be one of: {', '.join(map(str, rule.allowed_values))}")
            
        except (ValueError, TypeError):
            result.is_valid = False
            result.errors.append(f"{rule.field_name} must be a valid integer")
        
        return result
    
    @classmethod
    def validate_float(cls, value: Any, rule: ValidationRule) -> ValidationResult:
        """Validate float input"""
        result = ValidationResult(is_valid=True, original_value=value)
        
        if value is None:
            if rule.required:
                result.is_valid = False
                result.errors.append(f"{rule.field_name} is required")
                return result
            else:
                result.sanitized_value = 0.0
                return result
        
        try:
            if isinstance(value, str):
                # Remove whitespace and common formatting
                clean_value = value.strip().replace(',', '')
                float_value = float(clean_value)
            else:
                float_value = float(value)
            
            result.sanitized_value = float_value
            
            # Range validation
            if rule.min_value is not None and float_value < rule.min_value:
                result.is_valid = False
                result.errors.append(f"{rule.field_name} must be at least {rule.min_value}")
            
            if rule.max_value is not None and float_value > rule.max_value:
                result.is_valid = False
                result.errors.append(f"{rule.field_name} must not exceed {rule.max_value}")
            
        except (ValueError, TypeError):
            result.is_valid = False
            result.errors.append(f"{rule.field_name} must be a valid number")
        
        return result
    
    @classmethod
    def validate_boolean(cls, value: Any, rule: ValidationRule) -> ValidationResult:
        """Validate boolean input"""
        result = ValidationResult(is_valid=True, original_value=value)
        
        if value is None:
            if rule.required:
                result.is_valid = False
                result.errors.append(f"{rule.field_name} is required")
                return result
            else:
                result.sanitized_value = False
                return result
        
        # Convert various formats to boolean
        if isinstance(value, bool):
            result.sanitized_value = value
        elif isinstance(value, str):
            lower_value = value.lower().strip()
            if lower_value in ['true', '1', 'yes', 'on', 'enabled']:
                result.sanitized_value = True
            elif lower_value in ['false', '0', 'no', 'off', 'disabled']:
                result.sanitized_value = False
            else:
                result.is_valid = False
                result.errors.append(f"{rule.field_name} must be a valid boolean value")
        elif isinstance(value, (int, float)):
            result.sanitized_value = bool(value)
        else:
            result.is_valid = False
            result.errors.append(f"{rule.field_name} must be a valid boolean value")
        
        return result
    
    @classmethod
    def validate_email(cls, value: Any, rule: ValidationRule) -> ValidationResult:
        """Validate email input"""
        result = ValidationResult(is_valid=True, original_value=value)
        
        if value is None:
            if rule.required:
                result.is_valid = False
                result.errors.append(f"{rule.field_name} is required")
                return result
            else:
                result.sanitized_value = ""
                return result
        
        email_str = str(value).strip().lower()
        result.sanitized_value = email_str
        
        # Basic format validation
        if not re.match(cls.PATTERNS['email'], email_str):
            result.is_valid = False
            result.errors.append(f"{rule.field_name} must be a valid email address")
            return result
        
        # Additional validation using validators library
        try:
            if not validators.email(email_str):
                result.is_valid = False
                result.errors.append(f"{rule.field_name} must be a valid email address")
        except Exception:
            # Fallback to regex validation if validators fails
            pass
        
        # Length validation
        if len(email_str) > 254:  # RFC 5321 limit
            result.is_valid = False
            result.errors.append(f"{rule.field_name} email address is too long")
        
        return result
    
    @classmethod
    def validate_url(cls, value: Any, rule: ValidationRule) -> ValidationResult:
        """Validate URL input"""
        result = ValidationResult(is_valid=True, original_value=value)
        
        if value is None:
            if rule.required:
                result.is_valid = False
                result.errors.append(f"{rule.field_name} is required")
                return result
            else:
                result.sanitized_value = ""
                return result
        
        url_str = str(value).strip()
        result.sanitized_value = url_str
        
        try:
            # Parse URL
            parsed = urlparse(url_str)
            
            # Check scheme
            if not parsed.scheme:
                result.is_valid = False
                result.errors.append(f"{rule.field_name} must include a scheme (http/https)")
                return result
            
            allowed_schemes = rule.sanitization_options.get('allowed_schemes', ['http', 'https'])
            if parsed.scheme not in allowed_schemes:
                result.is_valid = False
                result.errors.append(f"{rule.field_name} scheme must be one of: {', '.join(allowed_schemes)}")
                return result
            
            # Check domain
            if not parsed.netloc:
                result.is_valid = False
                result.errors.append(f"{rule.field_name} must include a valid domain")
                return result
            
            # Validate using validators library
            if not validators.url(url_str):
                result.is_valid = False
                result.errors.append(f"{rule.field_name} must be a valid URL")
                return result
            
            # Security checks
            dangerous_domains = rule.sanitization_options.get('blocked_domains', ['localhost', '127.0.0.1', '0.0.0.0'])
            if any(domain in parsed.netloc.lower() for domain in dangerous_domains):
                result.is_valid = False
                result.errors.append(f"{rule.field_name} contains a blocked domain")
            
        except Exception:
            result.is_valid = False
            result.errors.append(f"{rule.field_name} must be a valid URL")
        
        return result
    
    @classmethod
    def validate_ip_address(cls, value: Any, rule: ValidationRule) -> ValidationResult:
        """Validate IP address input"""
        result = ValidationResult(is_valid=True, original_value=value)
        
        if value is None:
            if rule.required:
                result.is_valid = False
                result.errors.append(f"{rule.field_name} is required")
                return result
            else:
                result.sanitized_value = ""
                return result
        
        ip_str = str(value).strip()
        result.sanitized_value = ip_str
        
        try:
            # Try to parse as IPv4 or IPv6
            ip_obj = ipaddress.ip_address(ip_str)
            
            # Check version requirements
            allowed_versions = rule.sanitization_options.get('allowed_versions', [4, 6])
            if ip_obj.version not in allowed_versions:
                result.is_valid = False
                result.errors.append(f"{rule.field_name} must be IPv{'/IPv'.join(map(str, allowed_versions))} address")
                return result
            
            # Check if private/public requirements
            require_public = rule.sanitization_options.get('require_public', False)
            if require_public and ip_obj.is_private:
                result.is_valid = False
                result.errors.append(f"{rule.field_name} must be a public IP address")
            
            # Normalize the IP address
            result.sanitized_value = str(ip_obj)
            
        except ValueError:
            result.is_valid = False
            result.errors.append(f"{rule.field_name} must be a valid IP address")
        
        return result
    
    @classmethod
    def validate_date(cls, value: Any, rule: ValidationRule) -> ValidationResult:
        """Validate date input"""
        result = ValidationResult(is_valid=True, original_value=value)
        
        if value is None:
            if rule.required:
                result.is_valid = False
                result.errors.append(f"{rule.field_name} is required")
                return result
            else:
                result.sanitized_value = None
                return result
        
        try:
            if isinstance(value, date):
                result.sanitized_value = value
            elif isinstance(value, datetime):
                result.sanitized_value = value.date()
            elif isinstance(value, str):
                # Try common date formats
                date_formats = [
                    '%Y-%m-%d',
                    '%m/%d/%Y',
                    '%d/%m/%Y',
                    '%Y/%m/%d',
                    '%d-%m-%Y',
                    '%m-%d-%Y'
                ]
                
                date_str = value.strip()
                parsed_date = None
                
                for fmt in date_formats:
                    try:
                        parsed_date = datetime.strptime(date_str, fmt).date()
                        break
                    except ValueError:
                        continue
                
                if parsed_date is None:
                    result.is_valid = False
                    result.errors.append(f"{rule.field_name} must be a valid date")
                    return result
                
                result.sanitized_value = parsed_date
            else:
                result.is_valid = False
                result.errors.append(f"{rule.field_name} must be a valid date")
                return result
            
            # Date range validation
            if rule.min_value and result.sanitized_value < rule.min_value:
                result.is_valid = False
                result.errors.append(f"{rule.field_name} must be after {rule.min_value}")
            
            if rule.max_value and result.sanitized_value > rule.max_value:
                result.is_valid = False
                result.errors.append(f"{rule.field_name} must be before {rule.max_value}")
                
        except Exception as e:
            result.is_valid = False
            result.errors.append(f"{rule.field_name} date validation error: {str(e)}")
        
        return result
    
    @classmethod
    def validate_json(cls, value: Any, rule: ValidationRule) -> ValidationResult:
        """Validate JSON input"""
        result = ValidationResult(is_valid=True, original_value=value)
        
        if value is None:
            if rule.required:
                result.is_valid = False
                result.errors.append(f"{rule.field_name} is required")
                return result
            else:
                result.sanitized_value = {}
                return result
        
        try:
            if isinstance(value, str):
                # Parse JSON string
                parsed_json = json.loads(value)
                result.sanitized_value = parsed_json
            elif isinstance(value, (dict, list)):
                # Already parsed JSON
                result.sanitized_value = value
            else:
                result.is_valid = False
                result.errors.append(f"{rule.field_name} must be valid JSON")
                return result
            
            # Size limits
            max_depth = rule.sanitization_options.get('max_depth', 10)
            max_keys = rule.sanitization_options.get('max_keys', 1000)
            
            def check_depth(obj, current_depth=0):
                if current_depth > max_depth:
                    return False
                
                if isinstance(obj, dict):
                    if len(obj) > max_keys:
                        return False
                    return all(check_depth(v, current_depth + 1) for v in obj.values())
                elif isinstance(obj, list):
                    if len(obj) > max_keys:
                        return False
                    return all(check_depth(item, current_depth + 1) for item in obj)
                
                return True
            
            if not check_depth(result.sanitized_value):
                result.is_valid = False
                result.errors.append(f"{rule.field_name} JSON structure is too complex")
            
        except json.JSONDecodeError as e:
            result.is_valid = False
            result.errors.append(f"{rule.field_name} must be valid JSON: {str(e)}")
        except Exception as e:
            result.is_valid = False
            result.errors.append(f"{rule.field_name} JSON validation error: {str(e)}")
        
        return result
    
    @classmethod
    def validate_base64(cls, value: Any, rule: ValidationRule) -> ValidationResult:
        """Validate Base64 input"""
        result = ValidationResult(is_valid=True, original_value=value)
        
        if value is None:
            if rule.required:
                result.is_valid = False
                result.errors.append(f"{rule.field_name} is required")
                return result
            else:
                result.sanitized_value = ""
                return result
        
        try:
            b64_str = str(value).strip()
            
            # Decode to validate
            decoded = base64.b64decode(b64_str, validate=True)
            result.sanitized_value = b64_str
            
            # Size limits
            max_size = rule.sanitization_options.get('max_size', 10 * 1024 * 1024)  # 10MB default
            if len(decoded) > max_size:
                result.is_valid = False
                result.errors.append(f"{rule.field_name} decoded size exceeds limit")
            
        except Exception:
            result.is_valid = False
            result.errors.append(f"{rule.field_name} must be valid Base64")
        
        return result


class InputSanitizer:
    """Advanced input sanitization"""
    
    @staticmethod
    def sanitize_html(value: str, allowed_tags: List[str] = None, 
                     allowed_attributes: Dict[str, List[str]] = None) -> str:
        """
        Sanitize HTML input using bleach
        
        Args:
            value: HTML string to sanitize
            allowed_tags: List of allowed HTML tags
            allowed_attributes: Dictionary of allowed attributes per tag
            
        Returns:
            Sanitized HTML string
        """
        if not value:
            return ""
        
        if allowed_tags is None:
            allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'p', 'br', 'span']
        
        if allowed_attributes is None:
            allowed_attributes = {
                'span': ['class'],
                'p': ['class'],
            }
        
        # Use bleach for secure HTML sanitization
        sanitized = bleach.clean(
            value,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )
        
        return sanitized
    
    @staticmethod
    def sanitize_sql(value: str) -> str:
        """
        Sanitize SQL input
        
        Args:
            value: SQL string to sanitize
            
        Returns:
            Sanitized SQL string
        """
        if not value:
            return ""
        
        # Remove dangerous SQL patterns
        dangerous_patterns = [
            r'--.*$',           # SQL comments
            r'/\*.*?\*/',       # Block comments
            r';\s*$',           # Trailing semicolons
            r'\bEXEC\b',        # EXEC commands
            r'\bEXECUTE\b',     # EXECUTE commands
            r'\bsp_\w+',        # Stored procedures
            r'\bxp_\w+',        # Extended procedures
        ]
        
        sanitized = value
        for pattern in dangerous_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE | re.MULTILINE)
        
        # Escape single quotes
        sanitized = sanitized.replace("'", "''")
        
        return sanitized.strip()
    
    @staticmethod
    def sanitize_filename(value: str) -> str:
        """
        Sanitize filename
        
        Args:
            value: Filename to sanitize
            
        Returns:
            Sanitized filename
        """
        if not value:
            return ""
        
        # Remove path separators and dangerous characters
        dangerous_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '\0']
        sanitized = value
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '_')
        
        # Remove leading/trailing dots and spaces
        sanitized = sanitized.strip('. ')
        
        # Limit length
        if len(sanitized) > 255:
            name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
            max_name_len = 255 - len(ext) - 1 if ext else 255
            sanitized = name[:max_name_len] + ('.' + ext if ext else '')
        
        return sanitized
    
    @staticmethod
    def normalize_unicode(value: str) -> str:
        """
        Normalize Unicode string
        
        Args:
            value: String to normalize
            
        Returns:
            Normalized string
        """
        if not value:
            return ""
        
        # Normalize Unicode to NFC form
        normalized = unicodedata.normalize('NFC', value)
        
        # Remove control characters except common ones
        allowed_control = ['\t', '\n', '\r']
        cleaned = ''.join(
            char for char in normalized
            if not unicodedata.category(char).startswith('C') or char in allowed_control
        )
        
        return cleaned


class SchemaValidator:
    """Schema-based validation for complex data structures"""
    
    def __init__(self):
        self.input_validator = InputValidator()
        self.input_sanitizer = InputSanitizer()
    
    def validate_schema(self, data: Dict[str, Any], 
                       schema: Dict[str, ValidationRule]) -> Dict[str, ValidationResult]:
        """
        Validate data against schema
        
        Args:
            data: Data to validate
            schema: Schema definition with validation rules
            
        Returns:
            Dictionary of field validation results
        """
        results = {}
        
        # Validate each field in schema
        for field_name, rule in schema.items():
            value = data.get(field_name)
            
            # Route to appropriate validator based on data type
            if rule.data_type == DataType.STRING:
                result = self.input_validator.validate_string(value, rule)
            elif rule.data_type == DataType.INTEGER:
                result = self.input_validator.validate_integer(value, rule)
            elif rule.data_type == DataType.FLOAT:
                result = self.input_validator.validate_float(value, rule)
            elif rule.data_type == DataType.BOOLEAN:
                result = self.input_validator.validate_boolean(value, rule)
            elif rule.data_type == DataType.EMAIL:
                result = self.input_validator.validate_email(value, rule)
            elif rule.data_type == DataType.URL:
                result = self.input_validator.validate_url(value, rule)
            elif rule.data_type == DataType.IP_ADDRESS:
                result = self.input_validator.validate_ip_address(value, rule)
            elif rule.data_type == DataType.DATE:
                result = self.input_validator.validate_date(value, rule)
            elif rule.data_type == DataType.JSON:
                result = self.input_validator.validate_json(value, rule)
            elif rule.data_type == DataType.BASE64:
                result = self.input_validator.validate_base64(value, rule)
            else:
                # Default to string validation
                result = self.input_validator.validate_string(value, rule)
            
            # Apply sanitization if enabled and validation passed
            if rule.sanitize and result.is_valid and result.sanitized_value is not None:
                try:
                    if rule.data_type == DataType.HTML:
                        result.sanitized_value = self.input_sanitizer.sanitize_html(
                            str(result.sanitized_value),
                            rule.sanitization_options.get('allowed_tags'),
                            rule.sanitization_options.get('allowed_attributes')
                        )
                    elif rule.data_type == DataType.SQL:
                        result.sanitized_value = self.input_sanitizer.sanitize_sql(
                            str(result.sanitized_value)
                        )
                except Exception as e:
                    result.warnings.append(f"Sanitization warning: {str(e)}")
            
            results[field_name] = result
        
        # Check for unexpected fields
        unexpected_fields = set(data.keys()) - set(schema.keys())
        if unexpected_fields:
            for field in unexpected_fields:
                results[field] = ValidationResult(
                    is_valid=False,
                    errors=[f"Unexpected field: {field}"],
                    original_value=data[field]
                )
        
        return results
    
    def get_sanitized_data(self, validation_results: Dict[str, ValidationResult]) -> Dict[str, Any]:
        """
        Extract sanitized data from validation results
        
        Args:
            validation_results: Results from validate_schema
            
        Returns:
            Dictionary of sanitized data
        """
        sanitized_data = {}
        
        for field_name, result in validation_results.items():
            if result.is_valid and result.sanitized_value is not None:
                sanitized_data[field_name] = result.sanitized_value
        
        return sanitized_data
    
    def get_errors(self, validation_results: Dict[str, ValidationResult]) -> Dict[str, List[str]]:
        """
        Extract errors from validation results
        
        Args:
            validation_results: Results from validate_schema
            
        Returns:
            Dictionary of field errors
        """
        errors = {}
        
        for field_name, result in validation_results.items():
            if result.errors:
                errors[field_name] = result.errors
        
        return errors


# Usage example and common schemas
class CommonSchemas:
    """Common validation schemas"""
    
    @staticmethod
    def user_registration() -> Dict[str, ValidationRule]:
        """User registration schema"""
        return {
            'username': ValidationRule(
                field_name='username',
                data_type=DataType.STRING,
                required=True,
                min_length=3,
                max_length=20,
                pattern=r'^[a-zA-Z0-9_.-]+$'
            ),
            'email': ValidationRule(
                field_name='email',
                data_type=DataType.EMAIL,
                required=True
            ),
            'password': ValidationRule(
                field_name='password',
                data_type=DataType.STRING,
                required=True,
                min_length=8,
                pattern=r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$'
            ),
            'age': ValidationRule(
                field_name='age',
                data_type=DataType.INTEGER,
                required=False,
                min_value=13,
                max_value=120
            ),
            'terms_accepted': ValidationRule(
                field_name='terms_accepted',
                data_type=DataType.BOOLEAN,
                required=True,
                custom_validator=lambda x: x is True
            )
        }
    
    @staticmethod
    def api_search() -> Dict[str, ValidationRule]:
        """API search schema"""
        return {
            'query': ValidationRule(
                field_name='query',
                data_type=DataType.STRING,
                required=True,
                min_length=1,
                max_length=1000
            ),
            'limit': ValidationRule(
                field_name='limit',
                data_type=DataType.INTEGER,
                required=False,
                min_value=1,
                max_value=100
            ),
            'offset': ValidationRule(
                field_name='offset',
                data_type=DataType.INTEGER,
                required=False,
                min_value=0
            ),
            'sort_by': ValidationRule(
                field_name='sort_by',
                data_type=DataType.STRING,
                required=False,
                allowed_values=['relevance', 'date', 'title', 'author']
            ),
            'filters': ValidationRule(
                field_name='filters',
                data_type=DataType.JSON,
                required=False,
                sanitization_options={'max_depth': 3, 'max_keys': 50}
            )
        }


# Usage example:
if __name__ == "__main__":
    # Initialize validator
    validator = SchemaValidator()
    
    # Example user registration data
    user_data = {
        'username': 'john_doe',
        'email': 'john@example.com',
        'password': 'SecurePass123!',
        'age': 30,
        'terms_accepted': True
    }
    
    # Validate against schema
    schema = CommonSchemas.user_registration()
    results = validator.validate_schema(user_data, schema)
    
    # Check results
    all_valid = all(result.is_valid for result in results.values())
    print(f"All fields valid: {all_valid}")
    
    if all_valid:
        sanitized_data = validator.get_sanitized_data(results)
        print(f"Sanitized data: {sanitized_data}")
    else:
        errors = validator.get_errors(results)
        print(f"Validation errors: {errors}")
