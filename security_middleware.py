"""
Security Middleware for Business Intelligence Scraper
Implements rate limiting, security headers, input validation, and other security measures
"""

import re
import time
import json
from typing import Dict, Any, Optional
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""

    def __init__(self, app, enable_headers: bool = True, hsts_max_age: int = 31536000):
        super().__init__(app)
        self.enable_headers = enable_headers
        self.hsts_max_age = hsts_max_age

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        if self.enable_headers:
            # Strict Transport Security
            response.headers["Strict-Transport-Security"] = (
                f"max-age={self.hsts_max_age}; includeSubDomains"
            )

            # Content Security Policy
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "connect-src 'self' ws: wss:; "
                "frame-ancestors 'none';"
            )

            # Additional security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Permissions-Policy"] = (
                "geolocation=(), microphone=(), camera=()"
            )

            # Remove server information
            if "server" in response.headers:
                del response.headers["server"]

        return response


class InputValidationMiddleware(BaseHTTPMiddleware):
    """Validate and sanitize input to prevent common attacks"""

    # Common attack patterns
    SQL_INJECTION_PATTERNS = [
        r"(\bunion\b.*\bselect\b)",
        r"(\bselect\b.*\bfrom\b)",
        r"(\binsert\b.*\binto\b)",
        r"(\bdelete\b.*\bfrom\b)",
        r"(\bdrop\b.*\btable\b)",
        r"(\bexec\b.*\bsp_)",
        r"(\bor\b.*1\s*=\s*1)",
        r"('.*;\s*--)",
    ]

    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
    ]

    def __init__(self, app):
        super().__init__(app)
        self.sql_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.SQL_INJECTION_PATTERNS
        ]
        self.xss_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.XSS_PATTERNS
        ]

    async def dispatch(self, request: Request, call_next):
        # Skip validation for certain endpoints
        if request.url.path in ["/docs", "/openapi.json", "/favicon.ico"]:
            return await call_next(request)

        # Validate request body for POST/PUT requests
        if request.method in ["POST", "PUT", "PATCH"]:
            if "application/json" in request.headers.get("content-type", ""):
                try:
                    body = await request.body()
                    if body:
                        body_str = body.decode("utf-8")

                        # Check for SQL injection
                        if self._contains_sql_injection(body_str):
                            logger.warning(
                                f"SQL injection attempt detected from {request.client.host}"
                            )
                            raise HTTPException(
                                status_code=400, detail="Invalid input detected"
                            )

                        # Check for XSS
                        if self._contains_xss(body_str):
                            logger.warning(
                                f"XSS attempt detected from {request.client.host}"
                            )
                            raise HTTPException(
                                status_code=400, detail="Invalid input detected"
                            )

                        # Validate JSON structure
                        try:
                            json.loads(body_str)
                        except json.JSONDecodeError:
                            raise HTTPException(
                                status_code=400, detail="Invalid JSON format"
                            )

                        # Replace the request body for downstream processing
                        async def receive():
                            return {"type": "http.request", "body": body}

                        request._receive = receive

                except UnicodeDecodeError:
                    raise HTTPException(
                        status_code=400, detail="Invalid character encoding"
                    )

        # Validate query parameters
        for key, value in request.query_params.items():
            if self._contains_sql_injection(value) or self._contains_xss(value):
                logger.warning(
                    f"Malicious query parameter detected from {request.client.host}: {key}={value}"
                )
                raise HTTPException(status_code=400, detail="Invalid query parameter")

        return await call_next(request)

    def _contains_sql_injection(self, text: str) -> bool:
        """Check if text contains SQL injection patterns"""
        return any(pattern.search(text) for pattern in self.sql_patterns)

    def _contains_xss(self, text: str) -> bool:
        """Check if text contains XSS patterns"""
        return any(pattern.search(text) for pattern in self.xss_patterns)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests for security monitoring"""

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Log request
        client_ip = request.client.host if request.client else "unknown"
        logger.info(f"Request: {request.method} {request.url.path} from {client_ip}")

        response = await call_next(request)

        # Log response
        process_time = time.time() - start_time
        logger.info(f"Response: {response.status_code} in {process_time:.3f}s")

        # Log potential security issues
        if response.status_code >= 400:
            logger.warning(
                f"Error response {response.status_code} for {request.method} {request.url.path} from {client_ip}"
            )

        return response


# Rate limiting setup
def get_limiter(rate_limit_per_minute: int = 60) -> Limiter:
    """Create and configure rate limiter"""
    limiter = Limiter(
        key_func=get_remote_address, default_limits=[f"{rate_limit_per_minute}/minute"]
    )
    return limiter


def create_rate_limit_middleware(limiter: Limiter):
    """Create rate limiting middleware"""
    return SlowAPIMiddleware


class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """IP whitelist middleware for production environments"""

    def __init__(self, app, allowed_ips: Optional[list] = None):
        super().__init__(app)
        self.allowed_ips = allowed_ips or []

    async def dispatch(self, request: Request, call_next):
        if self.allowed_ips and request.client:
            client_ip = request.client.host
            if client_ip not in self.allowed_ips and not any(
                client_ip.startswith(allowed) for allowed in self.allowed_ips
            ):
                logger.warning(f"Access denied for IP: {client_ip}")
                raise HTTPException(status_code=403, detail="Access denied")

        return await call_next(request)


def sanitize_string(text: str, max_length: int = 1000) -> str:
    """Sanitize and validate string input"""
    if not isinstance(text, str):
        raise ValueError("Input must be a string")

    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length]

    # Remove null bytes and control characters
    text = "".join(
        char for char in text if ord(char) >= 32 or char in ["\n", "\r", "\t"]
    )

    # Basic HTML escaping
    text = (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )

    return text


def validate_url(url: str) -> bool:
    """Validate URL format and safety"""
    if not isinstance(url, str):
        return False

    # Basic URL pattern
    url_pattern = re.compile(
        r"^https?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    if not url_pattern.match(url):
        return False

    # Block dangerous protocols and domains
    dangerous_patterns = [
        r"file://",
        r"ftp://",
        r"localhost:(?!5173|3000|8000)",  # Only allow specific localhost ports
        r"127\.0\.0\.1:(?!5173|3000|8000)",  # Only allow specific local IPs
        r"\.local\b",
        r"\.internal\b",
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return False

    return True


def validate_job_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and sanitize job configuration"""
    if not isinstance(config, dict):
        raise ValueError("Configuration must be a dictionary")

    validated_config = {}

    # Validate URL
    if "url" in config:
        url = config["url"]
        if not validate_url(url):
            raise ValueError("Invalid or unsafe URL")
        validated_config["url"] = url

    # Validate scraper type
    if "scraper_type" in config:
        scraper_type = config["scraper_type"]
        allowed_types = ["basic", "e_commerce", "news", "social_media", "api"]
        if scraper_type not in allowed_types:
            raise ValueError(f"Invalid scraper type. Allowed: {allowed_types}")
        validated_config["scraper_type"] = scraper_type

    # Validate custom selectors
    if "config" in config and isinstance(config["config"], dict):
        if "custom_selectors" in config["config"]:
            selectors = config["config"]["custom_selectors"]
            if isinstance(selectors, dict):
                # Validate CSS selectors
                validated_selectors = {}
                for key, selector in selectors.items():
                    if isinstance(selector, str) and len(selector) <= 200:
                        # Basic CSS selector validation
                        if re.match(
                            r"^[a-zA-Z0-9\s\.\#\[\]\:\-\,\>\+\~\*\(\)=\"\']+$", selector
                        ):
                            validated_selectors[sanitize_string(key, 50)] = (
                                sanitize_string(selector, 200)
                            )
                validated_config["config"] = {"custom_selectors": validated_selectors}

    return validated_config


# Security utilities
def hash_password(password: str) -> str:
    """Hash password securely"""
    import bcrypt

    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    import bcrypt

    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def generate_secure_token() -> str:
    """Generate a cryptographically secure token"""
    import secrets

    return secrets.token_urlsafe(32)
