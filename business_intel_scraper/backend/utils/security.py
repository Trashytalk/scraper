"""
Enterprise Security Module for Visual Analytics Platform
OWASP compliance, vulnerability scanning, encryption, and comprehensive audit logging
"""

import hashlib
import hmac
import secrets
import bcrypt
import jwt
import re
import time
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import pyotp
import base64
import os
import ipaddress
from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import bleach
from sqlalchemy import text
import aioredis

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Security level classifications"""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

class ThreatType(Enum):
    """Types of security threats"""
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_BREACH = "data_breach"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    MALICIOUS_UPLOAD = "malicious_upload"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"

@dataclass
class SecurityEvent:
    """Security event data structure"""
    event_id: str
    event_type: ThreatType
    severity: SecurityLevel
    user_id: Optional[str]
    ip_address: str
    user_agent: str
    timestamp: datetime
    description: str
    metadata: Dict[str, Any]
    blocked: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            'event_type': self.event_type.value,
            'severity': self.severity.value,
            'timestamp': self.timestamp.isoformat()
        }

class EncryptionManager:
    """Advanced encryption and decryption management"""
    
    def __init__(self, master_key: Optional[str] = None):
        self.master_key = master_key or os.getenv('MASTER_ENCRYPTION_KEY')
        if not self.master_key:
            self.master_key = Fernet.generate_key().decode()
            logger.warning("Generated new master encryption key. Store this securely!")
        
        self.fernet = Fernet(self.master_key.encode())
        self.private_key = None
        self.public_key = None
        self._initialize_asymmetric_keys()
    
    def _initialize_asymmetric_keys(self):
        """Initialize RSA key pair for asymmetric encryption"""
        try:
            # Try to load existing keys
            private_key_path = "private_key.pem"
            public_key_path = "public_key.pem"
            
            if os.path.exists(private_key_path) and os.path.exists(public_key_path):
                with open(private_key_path, "rb") as f:
                    self.private_key = serialization.load_pem_private_key(
                        f.read(), password=None
                    )
                with open(public_key_path, "rb") as f:
                    self.public_key = serialization.load_pem_public_key(f.read())
            else:
                # Generate new keys
                self.private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048,
                )
                self.public_key = self.private_key.public_key()
                
                # Save keys
                with open(private_key_path, "wb") as f:
                    f.write(self.private_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.NoEncryption()
                    ))
                
                with open(public_key_path, "wb") as f:
                    f.write(self.public_key.public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    ))
                
                logger.info("Generated new RSA key pair")
                
        except Exception as e:
            logger.error(f"Error initializing asymmetric keys: {e}")
    
    def encrypt_data(self, data: Union[str, bytes]) -> str:
        """Encrypt data using symmetric encryption"""
        if isinstance(data, str):
            data = data.encode()
        
        encrypted = self.fernet.encrypt(data)
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data using symmetric encryption"""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            raise ValueError("Invalid encrypted data")
    
    def encrypt_asymmetric(self, data: Union[str, bytes]) -> str:
        """Encrypt data using RSA public key"""
        if isinstance(data, str):
            data = data.encode()
        
        encrypted = self.public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_asymmetric(self, encrypted_data: str) -> str:
        """Decrypt data using RSA private key"""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.private_key.decrypt(
                encrypted_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Asymmetric decryption error: {e}")
            raise ValueError("Invalid encrypted data")
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode(), salt)
        return hashed.decode()
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode(), hashed.encode())
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate cryptographically secure random token"""
        return secrets.token_urlsafe(length)
    
    def derive_key_from_password(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from password using PBKDF2"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return kdf.derive(password.encode())

class TwoFactorAuth:
    """Two-factor authentication management"""
    
    def __init__(self):
        self.issuer_name = "Visual Analytics Platform"
    
    def generate_secret(self) -> str:
        """Generate TOTP secret for new user"""
        return pyotp.random_base32()
    
    def generate_qr_code_url(self, user_email: str, secret: str) -> str:
        """Generate QR code URL for authenticator apps"""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=user_email,
            issuer_name=self.issuer_name
        )
    
    def verify_totp_token(self, secret: str, token: str, valid_window: int = 1) -> bool:
        """Verify TOTP token"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=valid_window)
    
    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """Generate backup codes for 2FA recovery"""
        return [secrets.token_hex(4) for _ in range(count)]

class InputValidator:
    """Input validation and sanitization"""
    
    # OWASP recommended patterns
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{3,20}$')
    PASSWORD_PATTERN = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')
    
    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        re.compile(r"(\bUNION\b.*\bSELECT\b)", re.IGNORECASE),
        re.compile(r"(\bSELECT\b.*\bFROM\b)", re.IGNORECASE),
        re.compile(r"(\bINSERT\b.*\bINTO\b)", re.IGNORECASE),
        re.compile(r"(\bUPDATE\b.*\bSET\b)", re.IGNORECASE),
        re.compile(r"(\bDELETE\b.*\bFROM\b)", re.IGNORECASE),
        re.compile(r"(\bDROP\b.*\bTABLE\b)", re.IGNORECASE),
        re.compile(r"(\bEXEC\b|\bEXECUTE\b)", re.IGNORECASE),
        re.compile(r"(--|\/\*|\*\/)", re.IGNORECASE),
    ]
    
    # XSS patterns
    XSS_PATTERNS = [
        re.compile(r"<script.*?>.*?</script>", re.IGNORECASE | re.DOTALL),
        re.compile(r"javascript:", re.IGNORECASE),
        re.compile(r"on\w+\s*=", re.IGNORECASE),
        re.compile(r"<iframe.*?>", re.IGNORECASE),
        re.compile(r"<object.*?>", re.IGNORECASE),
        re.compile(r"<embed.*?>", re.IGNORECASE),
    ]
    
    @classmethod
    def validate_email(cls, email: str) -> bool:
        """Validate email format"""
        if not email or len(email) > 254:
            return False
        return bool(cls.EMAIL_PATTERN.match(email))
    
    @classmethod
    def validate_username(cls, username: str) -> bool:
        """Validate username format"""
        return bool(cls.USERNAME_PATTERN.match(username)) if username else False
    
    @classmethod
    def validate_password(cls, password: str) -> Tuple[bool, List[str]]:
        """Validate password strength"""
        errors = []
        
        if not password:
            return False, ["Password is required"]
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if not re.search(r'[@$!%*?&]', password):
            errors.append("Password must contain at least one special character")
        
        return len(errors) == 0, errors
    
    @classmethod
    def detect_sql_injection(cls, input_string: str) -> bool:
        """Detect SQL injection attempts"""
        if not input_string:
            return False
        
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if pattern.search(input_string):
                return True
        return False
    
    @classmethod
    def detect_xss(cls, input_string: str) -> bool:
        """Detect XSS attempts"""
        if not input_string:
            return False
        
        for pattern in cls.XSS_PATTERNS:
            if pattern.search(input_string):
                return True
        return False
    
    @classmethod
    def sanitize_html(cls, html_content: str) -> str:
        """Sanitize HTML content to prevent XSS"""
        allowed_tags = [
            'p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote',
            'code', 'pre', 'a', 'img'
        ]
        
        allowed_attributes = {
            'a': ['href', 'title'],
            'img': ['src', 'alt', 'width', 'height'],
        }
        
        return bleach.clean(
            html_content,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )
    
    @classmethod
    def validate_file_upload(cls, filename: str, file_content: bytes) -> Tuple[bool, List[str]]:
        """Validate file uploads for security"""
        errors = []
        
        # Check file extension
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.txt', '.csv', '.json', '.xml'}
        file_ext = os.path.splitext(filename)[1].lower()
        
        if not file_ext:
            errors.append("File must have an extension")
        elif file_ext not in allowed_extensions:
            errors.append(f"File type {file_ext} not allowed")
        
        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if len(file_content) > max_size:
            errors.append("File size exceeds maximum limit of 10MB")
        
        # Check for malicious content
        dangerous_signatures = [
            b'<?php',
            b'<script',
            b'javascript:',
            b'<iframe',
            b'<object',
            b'<embed'
        ]
        
        content_lower = file_content[:1024].lower()  # Check first 1KB
        for sig in dangerous_signatures:
            if sig in content_lower:
                errors.append("File contains potentially malicious content")
                break
        
        return len(errors) == 0, errors

class SecurityAuditLogger:
    """Comprehensive security audit logging"""
    
    def __init__(self, encryption_manager: EncryptionManager):
        self.encryption_manager = encryption_manager
        self.security_events: List[SecurityEvent] = []
        self.blocked_ips: Dict[str, datetime] = {}
        self.failed_attempts: Dict[str, List[datetime]] = {}
        self.redis_client = None
    
    async def initialize_redis(self, redis_url: str):
        """Initialize Redis for distributed security tracking"""
        try:
            self.redis_client = await aioredis.from_url(redis_url)
            await self.redis_client.ping()
            logger.info("Security audit Redis initialized")
        except Exception as e:
            logger.warning(f"Redis unavailable for security logging: {e}")
    
    async def log_security_event(self, event: SecurityEvent):
        """Log security event with encryption"""
        # Encrypt sensitive metadata
        encrypted_metadata = {}
        for key, value in event.metadata.items():
            if key in ['password', 'token', 'session_id', 'api_key']:
                encrypted_metadata[key] = self.encryption_manager.encrypt_data(str(value))
            else:
                encrypted_metadata[key] = value
        
        event.metadata = encrypted_metadata
        
        # Store locally
        self.security_events.append(event)
        
        # Store in Redis if available
        if self.redis_client:
            try:
                await self.redis_client.lpush(
                    "security_events",
                    json.dumps(event.to_dict())
                )
                await self.redis_client.ltrim("security_events", 0, 9999)  # Keep last 10k events
            except Exception as e:
                logger.error(f"Error storing security event in Redis: {e}")
        
        # Log to file for compliance
        logger.warning(f"SECURITY EVENT: {event.event_type.value} - {event.description}")
        
        # Handle high-severity events
        if event.severity in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
            await self._handle_critical_event(event)
    
    async def _handle_critical_event(self, event: SecurityEvent):
        """Handle critical security events"""
        # Block IP for repeated offenses
        if event.event_type == ThreatType.BRUTE_FORCE:
            await self.block_ip(event.ip_address, duration=timedelta(hours=1))
        
        # Send alerts (implement your alerting system)
        await self._send_security_alert(event)
    
    async def _send_security_alert(self, event: SecurityEvent):
        """Send security alert (implement based on your alerting system)"""
        alert_message = f"""
        SECURITY ALERT - {event.severity.value.upper()}
        
        Event Type: {event.event_type.value}
        Time: {event.timestamp.isoformat()}
        IP Address: {event.ip_address}
        User ID: {event.user_id or 'Anonymous'}
        Description: {event.description}
        
        Please investigate immediately.
        """
        
        # TODO: Implement actual alerting (email, Slack, etc.)
        logger.critical(alert_message)
    
    async def track_failed_attempt(self, ip_address: str, user_id: str = None):
        """Track failed login attempts"""
        now = datetime.utcnow()
        key = f"{ip_address}:{user_id}" if user_id else ip_address
        
        if key not in self.failed_attempts:
            self.failed_attempts[key] = []
        
        # Clean old attempts (older than 1 hour)
        self.failed_attempts[key] = [
            attempt for attempt in self.failed_attempts[key]
            if (now - attempt).total_seconds() < 3600
        ]
        
        self.failed_attempts[key].append(now)
        
        # Check for brute force
        if len(self.failed_attempts[key]) >= 5:  # 5 attempts in 1 hour
            event = SecurityEvent(
                event_id=secrets.token_hex(16),
                event_type=ThreatType.BRUTE_FORCE,
                severity=SecurityLevel.HIGH,
                user_id=user_id,
                ip_address=ip_address,
                user_agent="",
                timestamp=now,
                description=f"Brute force detected: {len(self.failed_attempts[key])} failed attempts",
                metadata={'attempts': len(self.failed_attempts[key])},
                blocked=True
            )
            
            await self.log_security_event(event)
            return True  # Indicates brute force detected
        
        return False
    
    async def block_ip(self, ip_address: str, duration: timedelta):
        """Block IP address temporarily"""
        expiry = datetime.utcnow() + duration
        self.blocked_ips[ip_address] = expiry
        
        # Store in Redis if available
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    f"blocked_ip:{ip_address}",
                    int(duration.total_seconds()),
                    expiry.isoformat()
                )
            except Exception as e:
                logger.error(f"Error storing IP block in Redis: {e}")
        
        logger.warning(f"Blocked IP {ip_address} until {expiry}")
    
    async def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP address is blocked"""
        now = datetime.utcnow()
        
        # Check local cache
        if ip_address in self.blocked_ips:
            if self.blocked_ips[ip_address] > now:
                return True
            else:
                del self.blocked_ips[ip_address]
        
        # Check Redis if available
        if self.redis_client:
            try:
                blocked_until = await self.redis_client.get(f"blocked_ip:{ip_address}")
                if blocked_until:
                    expiry = datetime.fromisoformat(blocked_until.decode())
                    return expiry > now
            except Exception as e:
                logger.error(f"Error checking IP block in Redis: {e}")
        
        return False
    
    def get_security_report(self, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """Generate security audit report"""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=7)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Filter events by date range
        filtered_events = [
            event for event in self.security_events
            if start_date <= event.timestamp <= end_date
        ]
        
        # Analyze events
        event_counts = {}
        severity_counts = {}
        ip_counts = {}
        
        for event in filtered_events:
            event_type = event.event_type.value
            severity = event.severity.value
            ip = event.ip_address
            
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            ip_counts[ip] = ip_counts.get(ip, 0) + 1
        
        # Top threats
        top_ips = sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'report_period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'total_events': len(filtered_events),
            'event_types': event_counts,
            'severity_levels': severity_counts,
            'top_threat_ips': top_ips,
            'blocked_ips_count': len(self.blocked_ips),
            'failed_attempts_tracked': len(self.failed_attempts)
        }

class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware for FastAPI"""
    
    def __init__(self, app, audit_logger: SecurityAuditLogger):
        super().__init__(app)
        self.audit_logger = audit_logger
        self.rate_limits: Dict[str, List[datetime]] = {}
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Get client IP
        client_ip = request.client.host
        if "x-forwarded-for" in request.headers:
            client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
        
        # Check if IP is blocked
        if await self.audit_logger.is_ip_blocked(client_ip):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Rate limiting
        if await self._check_rate_limit(client_ip):
            event = SecurityEvent(
                event_id=secrets.token_hex(16),
                event_type=ThreatType.RATE_LIMIT_EXCEEDED,
                severity=SecurityLevel.MEDIUM,
                user_id=None,
                ip_address=client_ip,
                user_agent=request.headers.get("user-agent", ""),
                timestamp=datetime.utcnow(),
                description="Rate limit exceeded",
                metadata={'path': str(request.url.path)},
                blocked=True
            )
            await self.audit_logger.log_security_event(event)
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Validate request
        await self._validate_request(request, client_ip)
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        self._add_security_headers(response)
        
        # Log request
        process_time = time.time() - start_time
        logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
        
        return response
    
    async def _check_rate_limit(self, ip_address: str, limit: int = 100, window: int = 60) -> bool:
        """Check rate limiting (requests per minute)"""
        now = datetime.utcnow()
        
        if ip_address not in self.rate_limits:
            self.rate_limits[ip_address] = []
        
        # Clean old requests
        self.rate_limits[ip_address] = [
            req_time for req_time in self.rate_limits[ip_address]
            if (now - req_time).total_seconds() < window
        ]
        
        # Check limit
        if len(self.rate_limits[ip_address]) >= limit:
            return True  # Rate limit exceeded
        
        # Add current request
        self.rate_limits[ip_address].append(now)
        return False
    
    async def _validate_request(self, request: Request, client_ip: str):
        """Validate incoming request for security threats"""
        # Check for SQL injection in query parameters
        for param, value in request.query_params.items():
            if InputValidator.detect_sql_injection(value):
                event = SecurityEvent(
                    event_id=secrets.token_hex(16),
                    event_type=ThreatType.SQL_INJECTION,
                    severity=SecurityLevel.HIGH,
                    user_id=None,
                    ip_address=client_ip,
                    user_agent=request.headers.get("user-agent", ""),
                    timestamp=datetime.utcnow(),
                    description=f"SQL injection attempt in parameter: {param}",
                    metadata={'parameter': param, 'value': value},
                    blocked=True
                )
                await self.audit_logger.log_security_event(event)
                raise HTTPException(status_code=400, detail="Invalid request")
        
        # Check for XSS in headers
        for header, value in request.headers.items():
            if InputValidator.detect_xss(value):
                event = SecurityEvent(
                    event_id=secrets.token_hex(16),
                    event_type=ThreatType.XSS,
                    severity=SecurityLevel.HIGH,
                    user_id=None,
                    ip_address=client_ip,
                    user_agent=request.headers.get("user-agent", ""),
                    timestamp=datetime.utcnow(),
                    description=f"XSS attempt in header: {header}",
                    metadata={'header': header, 'value': value},
                    blocked=True
                )
                await self.audit_logger.log_security_event(event)
                raise HTTPException(status_code=400, detail="Invalid request")
    
    def _add_security_headers(self, response: Response):
        """Add security headers to response"""
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value

# Global security instances
encryption_manager = EncryptionManager()
two_factor_auth = TwoFactorAuth()
audit_logger = SecurityAuditLogger(encryption_manager)

# Export for easy import
__all__ = [
    'EncryptionManager', 'TwoFactorAuth', 'InputValidator', 'SecurityAuditLogger',
    'SecurityMiddleware', 'SecurityEvent', 'ThreatType', 'SecurityLevel',
    'encryption_manager', 'two_factor_auth', 'audit_logger'
]
