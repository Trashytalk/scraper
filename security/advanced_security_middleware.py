#!/usr/bin/env python3
"""
Advanced Security Middleware
Enhanced security features including intrusion detection, rate limiting, and threat analysis
"""

import time
import hmac
import hashlib
import ipaddress
import re
import json
import logging
from typing import Dict, List, Set, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict, deque
import asyncio
from functools import wraps

@dataclass
class SecurityEvent:
    """Security event data structure"""
    event_type: str
    severity: str  # low, medium, high, critical
    source_ip: str
    user_id: Optional[str]
    endpoint: str
    details: Dict[str, Any]
    timestamp: datetime
    
class ThreatDetector:
    """Advanced threat detection system"""
    
    def __init__(self):
        self.suspicious_patterns = [
            # SQL Injection patterns
            r"(\b(union|select|insert|update|delete|drop|create|alter)\b.*?\b(from|where|into)\b)",
            r"(--|#|/\*|\*/|;)",
            r"(\b(or|and)\b\s+\d+\s*=\s*\d+)",
            
            # XSS patterns
            r"(<script[^>]*>.*?</script>)",
            r"(javascript:|vbscript:|onload=|onerror=|onclick=)",
            r"(\balert\s*\(|\bconfirm\s*\(|\bprompt\s*\()",
            
            # Path traversal
            r"(\.\./|\.\.\\|%2e%2e%2f|%2e%2e%5c)",
            
            # Command injection
            r"(;|\||&|`|\$\(|\${|%0a|%0d)",
            
            # NoSQL injection
            r"(\$where|\$ne|\$gt|\$lt|\$regex|\$exists)",
        ]
        
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.suspicious_patterns]
        
    def analyze_request(self, method: str, path: str, headers: Dict[str, str], 
                       params: Dict[str, Any], body: str) -> List[str]:
        """Analyze request for security threats"""
        threats = []
        
        # Combine all text data for analysis
        text_data = f"{path} {json.dumps(params)} {body} {json.dumps(headers)}"
        
        # Check for suspicious patterns
        for i, pattern in enumerate(self.compiled_patterns):
            if pattern.search(text_data):
                threats.append(f"suspicious_pattern_{i}")
        
        # Check for oversized requests
        if len(body) > 10 * 1024 * 1024:  # 10MB
            threats.append("oversized_request")
        
        # Check for suspicious headers
        if 'user-agent' in headers and len(headers['user-agent']) > 1000:
            threats.append("suspicious_user_agent")
        
        # Check for too many parameters
        if len(params) > 100:
            threats.append("parameter_flooding")
        
        return threats

class RateLimiter:
    """Advanced rate limiting with multiple strategies"""
    
    def __init__(self):
        self.requests = defaultdict(deque)
        self.blocked_ips = {}
        self.user_requests = defaultdict(deque)
        
        # Rate limit configurations
        self.limits = {
            'global': {'requests': 1000, 'window': 3600},  # 1000 requests per hour
            'per_ip': {'requests': 100, 'window': 3600},   # 100 requests per IP per hour
            'per_user': {'requests': 500, 'window': 3600}, # 500 requests per user per hour
            'login': {'requests': 5, 'window': 900},       # 5 login attempts per 15 minutes
            'sensitive': {'requests': 10, 'window': 3600}, # 10 sensitive operations per hour
        }
    
    def is_rate_limited(self, key: str, limit_type: str = 'global') -> bool:
        """Check if a key is rate limited"""
        now = time.time()
        limit_config = self.limits.get(limit_type, self.limits['global'])
        window = limit_config['window']
        max_requests = limit_config['requests']
        
        # Get request queue for this key
        if limit_type == 'per_user':
            queue = self.user_requests[key]
        else:
            queue = self.requests[key]
        
        # Remove old requests outside the window
        while queue and queue[0] < now - window:
            queue.popleft()
        
        # Check if limit exceeded
        if len(queue) >= max_requests:
            return True
        
        # Add current request
        queue.append(now)
        return False
    
    def block_ip(self, ip: str, duration: int = 3600):
        """Block an IP address for a specific duration"""
        self.blocked_ips[ip] = time.time() + duration
    
    def is_ip_blocked(self, ip: str) -> bool:
        """Check if an IP is currently blocked"""
        if ip in self.blocked_ips:
            if time.time() < self.blocked_ips[ip]:
                return True
            else:
                del self.blocked_ips[ip]
        return False

class SecurityLogger:
    """Enhanced security event logging"""
    
    def __init__(self, log_file: str = "security.log"):
        self.logger = logging.getLogger('security')
        self.logger.setLevel(logging.INFO)
        
        # File handler for security logs
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter(
            '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler for immediate alerts
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '🚨 SECURITY ALERT: %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
    
    def log_event(self, event: SecurityEvent):
        """Log a security event"""
        event_data = {
            'type': event.event_type,
            'severity': event.severity,
            'source_ip': event.source_ip,
            'user_id': event.user_id,
            'endpoint': event.endpoint,
            'details': event.details,
            'timestamp': event.timestamp.isoformat()
        }
        
        log_message = f"{event.event_type} | {event.source_ip} | {event.endpoint} | {json.dumps(event.details)}"
        
        if event.severity == 'critical':
            self.logger.critical(log_message)
        elif event.severity == 'high':
            self.logger.error(log_message)
        elif event.severity == 'medium':
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)

class AdvancedSecurityMiddleware:
    """Comprehensive security middleware"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.threat_detector = ThreatDetector()
        self.rate_limiter = RateLimiter()
        self.security_logger = SecurityLogger()
        
        # IP whitelist and blacklist
        self.ip_whitelist = set(config.get('ip_whitelist', []))
        self.ip_blacklist = set(config.get('ip_blacklist', []))
        
        # Geo-blocking
        self.blocked_countries = set(config.get('blocked_countries', []))
        
        # Security headers
        self.security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
        }
    
    def extract_client_ip(self, request) -> str:
        """Extract real client IP address"""
        # Check for forwarded headers
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        return request.client.host if hasattr(request, 'client') else '127.0.0.1'
    
    def is_ip_allowed(self, ip: str) -> bool:
        """Check if IP is allowed based on whitelist/blacklist"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            
            # Check whitelist first
            if self.ip_whitelist:
                for allowed_ip in self.ip_whitelist:
                    if ip_obj in ipaddress.ip_network(allowed_ip, strict=False):
                        return True
                return False
            
            # Check blacklist
            for blocked_ip in self.ip_blacklist:
                if ip_obj in ipaddress.ip_network(blocked_ip, strict=False):
                    return False
            
            return True
            
        except ValueError:
            # Invalid IP format
            return False
    
    def validate_request_size(self, request) -> bool:
        """Validate request size limits"""
        content_length = request.headers.get('content-length')
        if content_length:
            try:
                size = int(content_length)
                max_size = self.config.get('max_request_size', 50 * 1024 * 1024)  # 50MB default
                return size <= max_size
            except ValueError:
                return False
        return True
    
    def check_request_signature(self, request, secret_key: str) -> bool:
        """Verify request signature for API authentication"""
        signature = request.headers.get('X-Signature')
        if not signature:
            return False
        
        # Get request body
        body = getattr(request, 'body', b'')
        if isinstance(body, str):
            body = body.encode('utf-8')
        
        # Calculate expected signature
        expected = hmac.new(
            secret_key.encode('utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures securely
        return hmac.compare_digest(signature, expected)
    
    async def process_request(self, request, response_callback):
        """Main security processing pipeline"""
        start_time = time.time()
        client_ip = self.extract_client_ip(request)
        user_id = getattr(request.state, 'user_id', None)
        
        try:
            # IP-based checks
            if not self.is_ip_allowed(client_ip):
                self.security_logger.log_event(SecurityEvent(
                    event_type='blocked_ip',
                    severity='high',
                    source_ip=client_ip,
                    user_id=user_id,
                    endpoint=request.url.path,
                    details={'reason': 'ip_blacklisted'},
                    timestamp=datetime.now()
                ))
                return self._create_security_response(403, "Access denied")
            
            # Check if IP is currently blocked
            if self.rate_limiter.is_ip_blocked(client_ip):
                self.security_logger.log_event(SecurityEvent(
                    event_type='blocked_request',
                    severity='medium',
                    source_ip=client_ip,
                    user_id=user_id,
                    endpoint=request.url.path,
                    details={'reason': 'ip_temporarily_blocked'},
                    timestamp=datetime.now()
                ))
                return self._create_security_response(429, "IP temporarily blocked")
            
            # Rate limiting checks
            if self.rate_limiter.is_rate_limited(client_ip, 'per_ip'):
                # Block IP for repeated violations
                self.rate_limiter.block_ip(client_ip, 3600)  # 1 hour
                
                self.security_logger.log_event(SecurityEvent(
                    event_type='rate_limit_exceeded',
                    severity='medium',
                    source_ip=client_ip,
                    user_id=user_id,
                    endpoint=request.url.path,
                    details={'limit_type': 'per_ip'},
                    timestamp=datetime.now()
                ))
                return self._create_security_response(429, "Rate limit exceeded")
            
            # Request size validation
            if not self.validate_request_size(request):
                self.security_logger.log_event(SecurityEvent(
                    event_type='oversized_request',
                    severity='medium',
                    source_ip=client_ip,
                    user_id=user_id,
                    endpoint=request.url.path,
                    details={'content_length': request.headers.get('content-length')},
                    timestamp=datetime.now()
                ))
                return self._create_security_response(413, "Request too large")
            
            # Threat detection
            body = ""
            if hasattr(request, 'body'):
                body = request.body.decode('utf-8') if isinstance(request.body, bytes) else str(request.body)
            
            threats = self.threat_detector.analyze_request(
                method=request.method,
                path=request.url.path,
                headers=dict(request.headers),
                params=dict(request.query_params),
                body=body
            )
            
            if threats:
                # Log security threats
                self.security_logger.log_event(SecurityEvent(
                    event_type='security_threat_detected',
                    severity='high',
                    source_ip=client_ip,
                    user_id=user_id,
                    endpoint=request.url.path,
                    details={'threats': threats, 'request_sample': body[:500]},
                    timestamp=datetime.now()
                ))
                
                # Block IP for security threats
                self.rate_limiter.block_ip(client_ip, 7200)  # 2 hours
                return self._create_security_response(403, "Security threat detected")
            
            # Process the request
            response = await response_callback(request)
            
            # Add security headers
            for header, value in self.security_headers.items():
                response.headers[header] = value
            
            # Log successful request (for analytics)
            processing_time = time.time() - start_time
            if processing_time > 5.0:  # Log slow requests
                self.security_logger.log_event(SecurityEvent(
                    event_type='slow_request',
                    severity='low',
                    source_ip=client_ip,
                    user_id=user_id,
                    endpoint=request.url.path,
                    details={'processing_time': processing_time},
                    timestamp=datetime.now()
                ))
            
            return response
            
        except Exception as e:
            # Log security middleware errors
            self.security_logger.log_event(SecurityEvent(
                event_type='security_middleware_error',
                severity='medium',
                source_ip=client_ip,
                user_id=user_id,
                endpoint=request.url.path,
                details={'error': str(e)},
                timestamp=datetime.now()
            ))
            
            # Continue with request on middleware error
            return await response_callback(request)
    
    def _create_security_response(self, status_code: int, message: str):
        """Create standardized security response"""
        from fastapi.responses import JSONResponse
        
        return JSONResponse(
            status_code=status_code,
            content={
                'error': message,
                'timestamp': datetime.now().isoformat(),
                'request_id': f"sec_{int(time.time())}"
            },
            headers=self.security_headers
        )

# Usage example and configuration
def create_security_middleware(config: Dict[str, Any]):
    """Factory function to create security middleware"""
    return AdvancedSecurityMiddleware(config)

# Decorator for endpoint-specific security
def require_security_level(level: str = 'medium'):
    """Decorator to enforce security levels on specific endpoints"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Additional security checks based on level
            request = kwargs.get('request') or args[0]
            
            if level == 'high':
                # Require additional authentication
                if not hasattr(request.state, 'user_id'):
                    raise HTTPException(status_code=401, detail="Authentication required")
                
                # Check for admin privileges
                if not getattr(request.state, 'is_admin', False):
                    raise HTTPException(status_code=403, detail="Admin access required")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

if __name__ == "__main__":
    # Example configuration
    config = {
        'max_request_size': 50 * 1024 * 1024,  # 50MB
        'ip_whitelist': ['127.0.0.1', '10.0.0.0/8'],
        'ip_blacklist': ['192.168.1.100'],
        'blocked_countries': ['CN', 'RU'],  # Example country codes
        'enable_geo_blocking': False,
        'log_all_requests': True,
        'alert_on_threats': True
    }
    
    # Create security middleware
    security_middleware = create_security_middleware(config)
    print("🛡️ Advanced Security Middleware initialized")
    print(f"   - IP Whitelist: {len(config.get('ip_whitelist', []))} entries")
    print(f"   - IP Blacklist: {len(config.get('ip_blacklist', []))} entries")
    print(f"   - Max Request Size: {config['max_request_size'] / (1024*1024):.1f} MB")
    print(f"   - Threat Detection: Enabled with {len(security_middleware.threat_detector.compiled_patterns)} patterns")
