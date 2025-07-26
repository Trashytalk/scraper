"""
Advanced Security Middleware
Comprehensive security controls, input validation, and threat protection
"""

import re
import html
import json
import hashlib
import secrets
import time
import ipaddress
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from functools import wraps
from urllib.parse import urlparse, parse_qs
import logging
from enum import Enum
import threading
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security threat levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatType(Enum):
    """Types of security threats"""
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    DIRECTORY_TRAVERSAL = "directory_traversal"
    COMMAND_INJECTION = "command_injection"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_PATTERNS = "suspicious_patterns"
    MALFORMED_REQUEST = "malformed_request"
    UNAUTHORIZED_ACCESS = "unauthorized_access"


@dataclass
class SecurityEvent:
    """Security event record"""
    timestamp: datetime
    threat_type: ThreatType
    severity: SecurityLevel
    source_ip: str
    user_agent: str
    request_path: str
    request_data: str
    user_id: Optional[str] = None
    blocked: bool = False
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RateLimitRule:
    """Rate limiting rule configuration"""
    name: str
    max_requests: int
    time_window: int  # seconds
    burst_allowance: int = 0
    block_duration: int = 300  # seconds


class InputSanitizer:
    """Advanced input sanitization and validation"""
    
    # XSS patterns
    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'vbscript:',
        r'onload\s*=',
        r'onerror\s*=',
        r'onclick\s*=',
        r'onmouseover\s*=',
        r'onfocus\s*=',
        r'onblur\s*=',
        r'<iframe[^>]*>',
        r'<object[^>]*>',
        r'<embed[^>]*>',
        r'<link[^>]*>',
        r'<meta[^>]*>',
        r'expression\s*\(',
        r'url\s*\(',
        r'@import',
        r'<style[^>]*>.*?</style>'
    ]
    
    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r"union\s+select",
        r"drop\s+table",
        r"delete\s+from",
        r"insert\s+into",
        r"update\s+\w+\s+set",
        r"exec\s*\(",
        r"execute\s*\(",
        r"sp_\w+",
        r"xp_\w+",
        r"--\s*$",
        r"/\*.*?\*/",
        r"'\s*or\s+'",
        r"'\s*and\s+'",
        r"'\s*union\s+'",
        r"'\s*having\s+'",
        r"'\s*group\s+by\s+'",
        r";\s*drop\s+",
        r";\s*delete\s+",
        r";\s*update\s+",
        r";\s*insert\s+"
    ]
    
    # Command injection patterns
    COMMAND_INJECTION_PATTERNS = [
        r';\s*rm\s+',
        r';\s*cat\s+',
        r';\s*ls\s+',
        r';\s*ps\s+',
        r';\s*kill\s+',
        r';\s*wget\s+',
        r';\s*curl\s+',
        r'\|\s*nc\s+',
        r'\|\s*netcat\s+',
        r'&&\s*rm\s+',
        r'`.*`',
        r'\$\(.*\)',
        r'>\s*/dev/',
        r'<\s*/dev/',
        r'/etc/passwd',
        r'/etc/shadow',
        r'\.\./',
        r'~/',
        r'\.\./\.\.'
    ]
    
    # Directory traversal patterns
    DIRECTORY_TRAVERSAL_PATTERNS = [
        r'\.\./.*\.\.',
        r'\.\.\\.*\.\.',
        r'/\.\./\.\.',
        r'\\\.\.\\\.\.',
        r'%2e%2e%2f',
        r'%2e%2e\\',
        r'%c0%ae%2e/',
        r'%c1%9c',
        r'/etc/',
        r'/proc/',
        r'/sys/',
        r'\\windows\\',
        r'\\system32\\',
        r'c:\\',
        r'd:\\',
        r'e:\\'
    ]
    
    @classmethod
    def detect_threats(cls, input_data: str) -> List[Tuple[ThreatType, str]]:
        """
        Detect security threats in input data
        
        Args:
            input_data: Input string to analyze
            
        Returns:
            List of (threat_type, matched_pattern) tuples
        """
        threats = []
        input_lower = input_data.lower()
        
        # Check for XSS
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, input_lower, re.IGNORECASE | re.DOTALL):
                threats.append((ThreatType.XSS, pattern))
        
        # Check for SQL injection
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, input_lower, re.IGNORECASE):
                threats.append((ThreatType.SQL_INJECTION, pattern))
        
        # Check for command injection
        for pattern in cls.COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, input_lower, re.IGNORECASE):
                threats.append((ThreatType.COMMAND_INJECTION, pattern))
        
        # Check for directory traversal
        for pattern in cls.DIRECTORY_TRAVERSAL_PATTERNS:
            if re.search(pattern, input_lower, re.IGNORECASE):
                threats.append((ThreatType.DIRECTORY_TRAVERSAL, pattern))
        
        return threats
    
    @classmethod
    def sanitize_html(cls, input_string: str, allowed_tags: Set[str] = None) -> str:
        """
        Sanitize HTML input
        
        Args:
            input_string: HTML string to sanitize
            allowed_tags: Set of allowed HTML tags
            
        Returns:
            Sanitized HTML string
        """
        if not input_string:
            return ""
        
        # Default allowed tags (very restrictive)
        if allowed_tags is None:
            allowed_tags = {'b', 'i', 'u', 'em', 'strong', 'p', 'br'}
        
        # Escape HTML entities
        sanitized = html.escape(input_string)
        
        # If no tags are allowed, return escaped string
        if not allowed_tags:
            return sanitized
        
        # Allow only specified tags (simplified implementation)
        for tag in allowed_tags:
            # Allow opening tags
            sanitized = re.sub(
                f'&lt;{tag}&gt;',
                f'<{tag}>',
                sanitized,
                flags=re.IGNORECASE
            )
            # Allow closing tags
            sanitized = re.sub(
                f'&lt;/{tag}&gt;',
                f'</{tag}>',
                sanitized,
                flags=re.IGNORECASE
            )
        
        return sanitized
    
    @classmethod
    def sanitize_sql(cls, input_string: str) -> str:
        """
        Sanitize SQL input by escaping dangerous characters
        
        Args:
            input_string: SQL string to sanitize
            
        Returns:
            Sanitized SQL string
        """
        if not input_string:
            return ""
        
        # Escape single quotes
        sanitized = input_string.replace("'", "''")
        
        # Remove dangerous characters and keywords
        dangerous_chars = [';', '--', '/*', '*/', 'xp_', 'sp_']
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized
    
    @classmethod
    def validate_email(cls, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @classmethod
    def validate_url(cls, url: str, allowed_schemes: Set[str] = None) -> bool:
        """
        Validate URL format and scheme
        
        Args:
            url: URL to validate
            allowed_schemes: Set of allowed URL schemes
            
        Returns:
            True if URL is valid and safe
        """
        if allowed_schemes is None:
            allowed_schemes = {'http', 'https'}
        
        try:
            parsed = urlparse(url)
            
            # Check scheme
            if parsed.scheme not in allowed_schemes:
                return False
            
            # Check for dangerous patterns
            dangerous_patterns = ['localhost', '127.0.0.1', '0.0.0.0', 'file://', 'ftp://']
            url_lower = url.lower()
            
            for pattern in dangerous_patterns:
                if pattern in url_lower:
                    return False
            
            return True
            
        except Exception:
            return False
    
    @classmethod
    def validate_json(cls, json_string: str, max_depth: int = 10) -> Tuple[bool, Optional[Dict]]:
        """
        Validate and parse JSON with depth protection
        
        Args:
            json_string: JSON string to validate
            max_depth: Maximum allowed nesting depth
            
        Returns:
            Tuple of (is_valid, parsed_data)
        """
        try:
            data = json.loads(json_string)
            
            # Check nesting depth
            def check_depth(obj, current_depth=0):
                if current_depth > max_depth:
                    return False
                
                if isinstance(obj, dict):
                    return all(check_depth(v, current_depth + 1) for v in obj.values())
                elif isinstance(obj, list):
                    return all(check_depth(item, current_depth + 1) for item in obj)
                
                return True
            
            if not check_depth(data):
                return False, None
            
            return True, data
            
        except (json.JSONDecodeError, RecursionError):
            return False, None


class RateLimiter:
    """Advanced rate limiting with multiple strategies"""
    
    def __init__(self):
        self.rules: Dict[str, RateLimitRule] = {}
        self.request_history: Dict[str, Dict[str, deque]] = defaultdict(lambda: defaultdict(deque))
        self.blocked_ips: Dict[str, datetime] = {}
        self.lock = threading.Lock()
    
    def add_rule(self, rule: RateLimitRule):
        """Add a rate limiting rule"""
        self.rules[rule.name] = rule
    
    def check_rate_limit(self, identifier: str, rule_name: str, 
                        request_time: datetime = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if request exceeds rate limit
        
        Args:
            identifier: Unique identifier (IP address, user ID, etc.)
            rule_name: Name of the rate limiting rule to apply
            request_time: Time of the request (default: now)
            
        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        if request_time is None:
            request_time = datetime.now(timezone.utc)
        
        with self.lock:
            # Check if IP is blocked
            if identifier in self.blocked_ips:
                if request_time < self.blocked_ips[identifier]:
                    return False, {
                        "blocked": True,
                        "block_expires": self.blocked_ips[identifier],
                        "reason": "IP blocked due to rate limit violations"
                    }
                else:
                    # Block expired
                    del self.blocked_ips[identifier]
            
            # Get rule
            rule = self.rules.get(rule_name)
            if not rule:
                return True, {"message": "No rate limit rule found"}
            
            # Get request history for this identifier and rule
            history = self.request_history[identifier][rule_name]
            
            # Remove old requests outside the time window
            cutoff_time = request_time - timedelta(seconds=rule.time_window)
            while history and history[0] < cutoff_time:
                history.popleft()
            
            # Check if limit exceeded
            current_count = len(history)
            
            if current_count >= rule.max_requests:
                # Block the identifier
                block_until = request_time + timedelta(seconds=rule.block_duration)
                self.blocked_ips[identifier] = block_until
                
                return False, {
                    "blocked": True,
                    "current_count": current_count,
                    "limit": rule.max_requests,
                    "window": rule.time_window,
                    "block_duration": rule.block_duration,
                    "block_expires": block_until
                }
            
            # Add current request to history
            history.append(request_time)
            
            return True, {
                "allowed": True,
                "current_count": current_count + 1,
                "limit": rule.max_requests,
                "window": rule.time_window,
                "remaining": rule.max_requests - current_count - 1
            }


class CSRFProtection:
    """CSRF (Cross-Site Request Forgery) protection"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.tokens: Dict[str, Tuple[str, datetime]] = {}
        self.token_expiry = timedelta(hours=24)
    
    def generate_token(self, session_id: str) -> str:
        """
        Generate CSRF token for session
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            CSRF token
        """
        # Generate random token
        token_data = f"{session_id}:{int(time.time())}:{secrets.token_urlsafe(32)}"
        token = hashlib.sha256(f"{self.secret_key}:{token_data}".encode()).hexdigest()
        
        # Store token with expiry
        expires_at = datetime.now(timezone.utc) + self.token_expiry
        self.tokens[session_id] = (token, expires_at)
        
        return token
    
    def verify_token(self, session_id: str, token: str) -> bool:
        """
        Verify CSRF token
        
        Args:
            session_id: Session identifier
            token: CSRF token to verify
            
        Returns:
            True if token is valid
        """
        if session_id not in self.tokens:
            return False
        
        stored_token, expires_at = self.tokens[session_id]
        
        # Check expiry
        if datetime.now(timezone.utc) > expires_at:
            del self.tokens[session_id]
            return False
        
        # Verify token
        return secrets.compare_digest(stored_token, token)
    
    def cleanup_expired_tokens(self):
        """Remove expired CSRF tokens"""
        now = datetime.now(timezone.utc)
        expired_sessions = [
            session_id for session_id, (_, expires_at) in self.tokens.items()
            if now > expires_at
        ]
        
        for session_id in expired_sessions:
            del self.tokens[session_id]


class SecurityMonitor:
    """Real-time security monitoring and threat detection"""
    
    def __init__(self, max_events: int = 10000):
        self.events: deque = deque(maxlen=max_events)
        self.threat_counts: Dict[str, Dict[ThreatType, int]] = defaultdict(lambda: defaultdict(int))
        self.suspicious_ips: Set[str] = set()
        self.lock = threading.Lock()
    
    def log_event(self, event: SecurityEvent):
        """Log a security event"""
        with self.lock:
            self.events.append(event)
            self.threat_counts[event.source_ip][event.threat_type] += 1
            
            # Mark IP as suspicious if it has multiple threat types
            ip_threats = len(self.threat_counts[event.source_ip])
            if ip_threats >= 3:
                self.suspicious_ips.add(event.source_ip)
        
        # Log to system logger
        logger.warning(
            f"Security event: {event.threat_type.value} from {event.source_ip} "
            f"({event.severity.value}) - {event.request_path}"
        )
    
    def get_threat_summary(self, time_window: timedelta = None) -> Dict[str, Any]:
        """
        Get threat summary for specified time window
        
        Args:
            time_window: Time window for analysis (default: last hour)
            
        Returns:
            Threat summary statistics
        """
        if time_window is None:
            time_window = timedelta(hours=1)
        
        cutoff_time = datetime.now(timezone.utc) - time_window
        
        with self.lock:
            recent_events = [
                event for event in self.events
                if event.timestamp > cutoff_time
            ]
        
        # Count threats by type
        threat_counts = defaultdict(int)
        severity_counts = defaultdict(int)
        ip_counts = defaultdict(int)
        
        for event in recent_events:
            threat_counts[event.threat_type.value] += 1
            severity_counts[event.severity.value] += 1
            ip_counts[event.source_ip] += 1
        
        return {
            "time_window": str(time_window),
            "total_events": len(recent_events),
            "threat_types": dict(threat_counts),
            "severity_levels": dict(severity_counts),
            "top_ips": dict(sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            "suspicious_ips": list(self.suspicious_ips)
        }
    
    def is_suspicious_ip(self, ip: str) -> bool:
        """Check if IP address is marked as suspicious"""
        return ip in self.suspicious_ips


class SecurityMiddleware:
    """Comprehensive security middleware"""
    
    def __init__(self, secret_key: str):
        self.input_sanitizer = InputSanitizer()
        self.rate_limiter = RateLimiter()
        self.csrf_protection = CSRFProtection(secret_key)
        self.security_monitor = SecurityMonitor()
        
        # Setup default rate limiting rules
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Setup default rate limiting rules"""
        rules = [
            RateLimitRule("api_general", 100, 60, 10, 300),  # 100 req/min
            RateLimitRule("api_auth", 10, 60, 2, 900),       # 10 auth req/min
            RateLimitRule("api_search", 50, 60, 5, 300),     # 50 search req/min
            RateLimitRule("api_upload", 5, 60, 1, 600),      # 5 upload req/min
        ]
        
        for rule in rules:
            self.rate_limiter.add_rule(rule)
    
    def validate_request(self, request_data: Dict[str, Any]) -> Tuple[bool, List[SecurityEvent]]:
        """
        Comprehensive request validation
        
        Args:
            request_data: Request data including headers, body, etc.
            
        Returns:
            Tuple of (is_safe, security_events)
        """
        events = []
        is_safe = True
        
        # Extract request information
        ip_address = request_data.get('ip_address', 'unknown')
        user_agent = request_data.get('user_agent', '')
        path = request_data.get('path', '')
        method = request_data.get('method', 'GET')
        headers = request_data.get('headers', {})
        body = request_data.get('body', '')
        params = request_data.get('params', {})
        
        # Check rate limiting
        rule_name = self._get_rate_limit_rule(path)
        rate_allowed, rate_info = self.rate_limiter.check_rate_limit(ip_address, rule_name)
        
        if not rate_allowed:
            event = SecurityEvent(
                timestamp=datetime.now(timezone.utc),
                threat_type=ThreatType.RATE_LIMIT_EXCEEDED,
                severity=SecurityLevel.HIGH,
                source_ip=ip_address,
                user_agent=user_agent,
                request_path=path,
                request_data=str(request_data),
                blocked=True,
                details=rate_info
            )
            events.append(event)
            is_safe = False
        
        # Validate all input fields
        all_inputs = []
        
        # Add body content
        if body:
            all_inputs.append(('body', body))
        
        # Add URL parameters
        for key, value in params.items():
            all_inputs.append((f'param_{key}', str(value)))
        
        # Add headers (selective)
        security_relevant_headers = ['referer', 'origin', 'x-forwarded-for']
        for header in security_relevant_headers:
            if header in headers:
                all_inputs.append((f'header_{header}', headers[header]))
        
        # Check each input for threats
        for input_name, input_value in all_inputs:
            threats = self.input_sanitizer.detect_threats(input_value)
            
            for threat_type, pattern in threats:
                severity = self._get_threat_severity(threat_type)
                
                event = SecurityEvent(
                    timestamp=datetime.now(timezone.utc),
                    threat_type=threat_type,
                    severity=severity,
                    source_ip=ip_address,
                    user_agent=user_agent,
                    request_path=path,
                    request_data=f"{input_name}: {input_value[:100]}...",
                    blocked=severity in [SecurityLevel.HIGH, SecurityLevel.CRITICAL],
                    details={
                        "input_field": input_name,
                        "matched_pattern": pattern,
                        "input_preview": input_value[:200]
                    }
                )
                events.append(event)
                
                if event.blocked:
                    is_safe = False
        
        # Check for suspicious patterns
        if self._detect_suspicious_patterns(request_data):
            event = SecurityEvent(
                timestamp=datetime.now(timezone.utc),
                threat_type=ThreatType.SUSPICIOUS_PATTERNS,
                severity=SecurityLevel.MEDIUM,
                source_ip=ip_address,
                user_agent=user_agent,
                request_path=path,
                request_data=str(request_data),
                blocked=False,
                details={"reason": "Suspicious request patterns detected"}
            )
            events.append(event)
        
        # Log all events
        for event in events:
            self.security_monitor.log_event(event)
        
        return is_safe, events
    
    def sanitize_input(self, input_data: Any, input_type: str = "text") -> Any:
        """
        Sanitize input based on type
        
        Args:
            input_data: Input data to sanitize
            input_type: Type of input (text, html, json, etc.)
            
        Returns:
            Sanitized input data
        """
        if input_data is None:
            return None
        
        if input_type == "html":
            return self.input_sanitizer.sanitize_html(str(input_data))
        elif input_type == "sql":
            return self.input_sanitizer.sanitize_sql(str(input_data))
        elif input_type == "json":
            if isinstance(input_data, str):
                is_valid, parsed = self.input_sanitizer.validate_json(input_data)
                return parsed if is_valid else None
            return input_data
        elif input_type == "email":
            email_str = str(input_data)
            return email_str if self.input_sanitizer.validate_email(email_str) else None
        elif input_type == "url":
            url_str = str(input_data)
            return url_str if self.input_sanitizer.validate_url(url_str) else None
        else:
            # Default text sanitization
            return html.escape(str(input_data))
    
    def generate_csrf_token(self, session_id: str) -> str:
        """Generate CSRF token for session"""
        return self.csrf_protection.generate_token(session_id)
    
    def verify_csrf_token(self, session_id: str, token: str) -> bool:
        """Verify CSRF token"""
        return self.csrf_protection.verify_token(session_id, token)
    
    def get_security_headers(self) -> Dict[str, str]:
        """
        Get recommended security headers
        
        Returns:
            Dictionary of security headers
        """
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-ancestors 'none';"
            ),
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }
    
    def _get_rate_limit_rule(self, path: str) -> str:
        """Determine rate limiting rule based on request path"""
        if '/auth/' in path or '/login' in path:
            return "api_auth"
        elif '/search' in path:
            return "api_search"
        elif '/upload' in path:
            return "api_upload"
        else:
            return "api_general"
    
    def _get_threat_severity(self, threat_type: ThreatType) -> SecurityLevel:
        """Determine severity level for threat type"""
        high_severity = [
            ThreatType.SQL_INJECTION,
            ThreatType.COMMAND_INJECTION,
            ThreatType.UNAUTHORIZED_ACCESS
        ]
        
        medium_severity = [
            ThreatType.XSS,
            ThreatType.CSRF,
            ThreatType.DIRECTORY_TRAVERSAL,
            ThreatType.RATE_LIMIT_EXCEEDED
        ]
        
        if threat_type in high_severity:
            return SecurityLevel.HIGH
        elif threat_type in medium_severity:
            return SecurityLevel.MEDIUM
        else:
            return SecurityLevel.LOW
    
    def _detect_suspicious_patterns(self, request_data: Dict[str, Any]) -> bool:
        """Detect suspicious request patterns"""
        suspicious_indicators = [
            # Unusual user agents
            lambda d: 'user_agent' in d and (
                len(d['user_agent']) > 500 or
                'bot' in d['user_agent'].lower() or
                'crawler' in d['user_agent'].lower()
            ),
            
            # Unusual request sizes
            lambda d: 'body' in d and len(str(d['body'])) > 100000,
            
            # Too many parameters
            lambda d: 'params' in d and len(d['params']) > 50,
            
            # Suspicious IP patterns
            lambda d: 'ip_address' in d and self.security_monitor.is_suspicious_ip(d['ip_address'])
        ]
        
        return any(indicator(request_data) for indicator in suspicious_indicators)


# Security decorator for protecting endpoints
def secure_endpoint(rate_limit_rule: str = "api_general", 
                   require_csrf: bool = True,
                   sanitize_inputs: bool = True):
    """
    Decorator for securing API endpoints
    
    Args:
        rate_limit_rule: Rate limiting rule to apply
        require_csrf: Whether to require CSRF token
        sanitize_inputs: Whether to sanitize input data
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # This would be implemented in the actual web framework
            # For now, it's a placeholder for the security logic
            
            # Get security middleware instance
            security_middleware = kwargs.get('security_middleware')
            if not security_middleware:
                raise SecurityError("Security middleware not available")
            
            # Get request data
            request_data = kwargs.get('request_data', {})
            
            # Validate request
            is_safe, events = security_middleware.validate_request(request_data)
            if not is_safe:
                blocked_events = [e for e in events if e.blocked]
                if blocked_events:
                    raise SecurityViolation(f"Request blocked due to security threats: {[e.threat_type.value for e in blocked_events]}")
            
            # CSRF protection
            if require_csrf and request_data.get('method', 'GET') in ['POST', 'PUT', 'DELETE']:
                session_id = request_data.get('session_id')
                csrf_token = request_data.get('csrf_token')
                
                if not session_id or not csrf_token:
                    raise SecurityViolation("CSRF token required")
                
                if not security_middleware.verify_csrf_token(session_id, csrf_token):
                    raise SecurityViolation("Invalid CSRF token")
            
            # Input sanitization
            if sanitize_inputs and 'body' in request_data:
                request_data['body'] = security_middleware.sanitize_input(
                    request_data['body'], 
                    request_data.get('content_type', 'text')
                )
                kwargs['request_data'] = request_data
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


class SecurityError(Exception):
    """Security-related error"""
    pass


class SecurityViolation(SecurityError):
    """Security violation error"""
    pass


# Usage example:
if __name__ == "__main__":
    # Initialize security middleware
    security = SecurityMiddleware(secret_key="your-secret-key-here")
    
    # Example request validation
    request_data = {
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0...",
        "path": "/api/data",
        "method": "GET",
        "params": {"query": "test"},
        "headers": {"referer": "https://example.com"},
        "body": ""
    }
    
    is_safe, events = security.validate_request(request_data)
    print(f"Request is safe: {is_safe}")
    print(f"Security events: {len(events)}")
    
    # Get security summary
    summary = security.security_monitor.get_threat_summary()
    print(f"Threat summary: {summary}")
    
    # Get security headers
    headers = security.get_security_headers()
    print(f"Security headers: {headers}")
