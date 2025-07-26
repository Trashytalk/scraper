"""
Enhanced Authentication System
Comprehensive authentication with JWT, OAuth2, MFA, and session management
"""

import jwt
import hashlib
import secrets
import pyotp
import qrcode
import base64
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Optional, Dict, Any, Tuple, List
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import re
from io import BytesIO
import bcrypt

logger = logging.getLogger(__name__)


class UserRole(Enum):
    """User role definitions with hierarchical permissions"""
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"
    GUEST = "guest"


class AuthenticationError(Exception):
    """Custom authentication exception"""
    pass


class SecurityViolation(Exception):
    """Security violation exception"""
    pass


@dataclass
class User:
    """Enhanced user model with security features"""
    id: str
    username: str
    email: str
    password_hash: str
    role: UserRole
    is_active: bool = True
    is_verified: bool = False
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None
    created_at: datetime = None
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    password_changed_at: datetime = None
    session_tokens: List[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.password_changed_at is None:
            self.password_changed_at = datetime.now(timezone.utc)
        if self.session_tokens is None:
            self.session_tokens = []


@dataclass
class SessionToken:
    """Secure session token with metadata"""
    token: str
    user_id: str
    issued_at: datetime
    expires_at: datetime
    ip_address: str
    user_agent: str
    is_active: bool = True
    last_activity: datetime = None
    refresh_token: Optional[str] = None


class SecurityConfig:
    """Security configuration constants"""
    # Password requirements
    MIN_PASSWORD_LENGTH = 12
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_NUMBERS = True
    REQUIRE_SPECIAL_CHARS = True
    
    # JWT settings
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    # Account lockout
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 30
    
    # Session management
    MAX_CONCURRENT_SESSIONS = 3
    SESSION_TIMEOUT_MINUTES = 60
    
    # MFA settings
    MFA_ISSUER = "Business Intelligence Scraper"
    MFA_CODE_VALIDITY_SECONDS = 30
    
    # Rate limiting
    LOGIN_RATE_LIMIT = 10  # attempts per minute
    API_RATE_LIMIT = 100   # requests per minute


class PasswordValidator:
    """Advanced password validation and strength checking"""
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, List[str]]:
        """
        Comprehensive password validation
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Length check
        if len(password) < SecurityConfig.MIN_PASSWORD_LENGTH:
            errors.append(f"Password must be at least {SecurityConfig.MIN_PASSWORD_LENGTH} characters long")
        
        # Character requirements
        if SecurityConfig.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
            
        if SecurityConfig.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
            
        if SecurityConfig.REQUIRE_NUMBERS and not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
            
        if SecurityConfig.REQUIRE_SPECIAL_CHARS and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        # Common password patterns
        common_patterns = [
            r'(.)\1{3,}',  # Repeated characters
            r'(012|123|234|345|456|567|678|789|890)',  # Sequential numbers
            r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)',  # Sequential letters
        ]
        
        for pattern in common_patterns:
            if re.search(pattern, password.lower()):
                errors.append("Password contains common patterns and is not secure")
                break
        
        # Dictionary words check (simplified)
        common_words = ['password', 'admin', 'user', 'login', 'welcome', 'secret', 'company']
        if any(word in password.lower() for word in common_words):
            errors.append("Password contains common dictionary words")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def calculate_strength(password: str) -> Dict[str, Any]:
        """
        Calculate password strength score
        
        Args:
            password: Password to analyze
            
        Returns:
            Dictionary with strength metrics
        """
        score = 0
        feedback = []
        
        # Length scoring
        if len(password) >= 16:
            score += 25
        elif len(password) >= 12:
            score += 15
        else:
            score += 5
            feedback.append("Consider using a longer password")
        
        # Character variety
        char_types = 0
        if re.search(r'[a-z]', password):
            char_types += 1
        if re.search(r'[A-Z]', password):
            char_types += 1
        if re.search(r'\d', password):
            char_types += 1
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            char_types += 1
        
        score += char_types * 15
        
        # Entropy calculation (simplified)
        unique_chars = len(set(password))
        if unique_chars > len(password) * 0.7:
            score += 20
            feedback.append("Good character variety")
        
        # Penalty for common patterns
        if re.search(r'(.)\1{2,}', password):
            score -= 10
            feedback.append("Avoid repeated characters")
        
        strength_level = "Very Weak"
        if score >= 80:
            strength_level = "Very Strong"
        elif score >= 60:
            strength_level = "Strong"
        elif score >= 40:
            strength_level = "Moderate"
        elif score >= 20:
            strength_level = "Weak"
        
        return {
            "score": min(100, max(0, score)),
            "strength": strength_level,
            "feedback": feedback
        }


class MFAManager:
    """Multi-Factor Authentication management"""
    
    @staticmethod
    def generate_secret() -> str:
        """Generate a new TOTP secret"""
        return pyotp.random_base32()
    
    @staticmethod
    def generate_qr_code(user_email: str, secret: str) -> str:
        """
        Generate QR code for MFA setup
        
        Args:
            user_email: User's email address
            secret: TOTP secret
            
        Returns:
            Base64 encoded QR code image
        """
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user_email,
            issuer_name=SecurityConfig.MFA_ISSUER
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    @staticmethod
    def verify_totp(secret: str, token: str, window: int = 1) -> bool:
        """
        Verify TOTP token
        
        Args:
            secret: User's TOTP secret
            token: Token to verify
            window: Time window for verification (default: 1 = 30 seconds)
            
        Returns:
            True if token is valid
        """
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(token, valid_window=window)
        except Exception as e:
            logger.error(f"TOTP verification error: {e}")
            return False
    
    @staticmethod
    def generate_backup_codes(count: int = 10) -> List[str]:
        """
        Generate backup codes for MFA recovery
        
        Args:
            count: Number of backup codes to generate
            
        Returns:
            List of backup codes
        """
        return [secrets.token_hex(4).upper() for _ in range(count)]


class AuthenticationManager:
    """Enhanced authentication manager with comprehensive security features"""
    
    def __init__(self, secret_key: str, db_manager=None):
        self.secret_key = secret_key
        self.db_manager = db_manager
        self.active_sessions: Dict[str, SessionToken] = {}
        self.rate_limiter: Dict[str, List[datetime]] = {}
        self.password_validator = PasswordValidator()
        self.mfa_manager = MFAManager()
    
    def hash_password(self, password: str) -> str:
        """
        Hash password using bcrypt
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify password against hash
        
        Args:
            password: Plain text password
            password_hash: Stored password hash
            
        Returns:
            True if password matches
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def create_user(self, username: str, email: str, password: str, role: UserRole) -> User:
        """
        Create new user with security validation
        
        Args:
            username: Unique username
            email: User email address
            password: Plain text password
            role: User role
            
        Returns:
            Created user object
            
        Raises:
            AuthenticationError: If validation fails
        """
        # Validate password
        is_valid, errors = self.password_validator.validate_password(password)
        if not is_valid:
            raise AuthenticationError(f"Password validation failed: {', '.join(errors)}")
        
        # Check if user exists
        if self.db_manager and self.db_manager.get_user_by_username(username):
            raise AuthenticationError("Username already exists")
        
        if self.db_manager and self.db_manager.get_user_by_email(email):
            raise AuthenticationError("Email already exists")
        
        # Create user
        user = User(
            id=secrets.token_urlsafe(16),
            username=username,
            email=email,
            password_hash=self.hash_password(password),
            role=role
        )
        
        # Save to database
        if self.db_manager:
            self.db_manager.create_user(user)
        
        logger.info(f"Created new user: {username} with role: {role.value}")
        return user
    
    def authenticate_user(self, username: str, password: str, ip_address: str = None, 
                         user_agent: str = None, mfa_token: str = None) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Comprehensive user authentication
        
        Args:
            username: Username or email
            password: Plain text password
            ip_address: Client IP address
            user_agent: Client user agent
            mfa_token: MFA token (if MFA is enabled)
            
        Returns:
            Tuple of (success, user_data_or_error)
        """
        try:
            # Rate limiting check
            if not self._check_rate_limit(ip_address or "unknown"):
                return False, {"error": "Rate limit exceeded", "retry_after": 60}
            
            # Get user
            user = None
            if self.db_manager:
                user = (self.db_manager.get_user_by_username(username) or 
                       self.db_manager.get_user_by_email(username))
            
            if not user:
                logger.warning(f"Authentication attempt for non-existent user: {username}")
                return False, {"error": "Invalid credentials"}
            
            # Check account lock
            if user.locked_until and datetime.now(timezone.utc) < user.locked_until:
                return False, {"error": "Account is locked", "locked_until": user.locked_until}
            
            # Verify password
            if not self.verify_password(password, user.password_hash):
                self._handle_failed_login(user)
                return False, {"error": "Invalid credentials"}
            
            # Check if account is active
            if not user.is_active:
                return False, {"error": "Account is disabled"}
            
            # MFA verification
            if user.mfa_enabled:
                if not mfa_token:
                    return False, {"error": "MFA token required", "requires_mfa": True}
                
                if not self.mfa_manager.verify_totp(user.mfa_secret, mfa_token):
                    self._handle_failed_login(user)
                    return False, {"error": "Invalid MFA token"}
            
            # Successful authentication
            self._handle_successful_login(user)
            
            # Generate session tokens
            access_token = self._generate_access_token(user)
            refresh_token = self._generate_refresh_token(user)
            
            # Create session
            session_token = SessionToken(
                token=access_token,
                user_id=user.id,
                issued_at=datetime.now(timezone.utc),
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=SecurityConfig.ACCESS_TOKEN_EXPIRE_MINUTES),
                ip_address=ip_address or "unknown",
                user_agent=user_agent or "unknown",
                refresh_token=refresh_token
            )
            
            self._manage_user_sessions(user.id, session_token)
            
            return True, {
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role.value,
                    "mfa_enabled": user.mfa_enabled
                },
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_in": SecurityConfig.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False, {"error": "Authentication failed"}
    
    def verify_token(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Verify JWT access token
        
        Args:
            token: JWT access token
            
        Returns:
            Tuple of (is_valid, user_data)
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[SecurityConfig.JWT_ALGORITHM])
            
            # Check if session is active
            session = self.active_sessions.get(token)
            if not session or not session.is_active:
                return False, None
            
            # Check expiration
            if datetime.now(timezone.utc) > session.expires_at:
                self._invalidate_session(token)
                return False, None
            
            # Update last activity
            session.last_activity = datetime.now(timezone.utc)
            
            return True, payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return False, None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return False, None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return False, None
    
    def refresh_token(self, refresh_token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            Tuple of (success, new_tokens_or_error)
        """
        try:
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=[SecurityConfig.JWT_ALGORITHM])
            
            if payload.get("type") != "refresh":
                return False, {"error": "Invalid token type"}
            
            user_id = payload.get("user_id")
            if not user_id:
                return False, {"error": "Invalid token"}
            
            # Get user
            user = self.db_manager.get_user_by_id(user_id) if self.db_manager else None
            if not user or not user.is_active:
                return False, {"error": "User not found or inactive"}
            
            # Generate new tokens
            new_access_token = self._generate_access_token(user)
            new_refresh_token = self._generate_refresh_token(user)
            
            return True, {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "expires_in": SecurityConfig.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
            
        except jwt.ExpiredSignatureError:
            return False, {"error": "Refresh token has expired"}
        except jwt.InvalidTokenError:
            return False, {"error": "Invalid refresh token"}
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return False, {"error": "Token refresh failed"}
    
    def logout(self, token: str) -> bool:
        """
        Logout user and invalidate session
        
        Args:
            token: Access token to invalidate
            
        Returns:
            True if successful
        """
        try:
            self._invalidate_session(token)
            logger.info("User logged out successfully")
            return True
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False
    
    def enable_mfa(self, user_id: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Enable MFA for user
        
        Args:
            user_id: User ID
            
        Returns:
            Tuple of (success, mfa_setup_data)
        """
        try:
            user = self.db_manager.get_user_by_id(user_id) if self.db_manager else None
            if not user:
                return False, {"error": "User not found"}
            
            if user.mfa_enabled:
                return False, {"error": "MFA already enabled"}
            
            # Generate secret
            secret = self.mfa_manager.generate_secret()
            qr_code = self.mfa_manager.generate_qr_code(user.email, secret)
            backup_codes = self.mfa_manager.generate_backup_codes()
            
            # Store secret (temporarily until verification)
            user.mfa_secret = secret
            
            if self.db_manager:
                self.db_manager.update_user(user)
            
            return True, {
                "secret": secret,
                "qr_code": qr_code,
                "backup_codes": backup_codes
            }
            
        except Exception as e:
            logger.error(f"MFA enable error: {e}")
            return False, {"error": "Failed to enable MFA"}
    
    def verify_mfa_setup(self, user_id: str, token: str) -> bool:
        """
        Verify MFA setup with TOTP token
        
        Args:
            user_id: User ID
            token: TOTP token
            
        Returns:
            True if verification successful
        """
        try:
            user = self.db_manager.get_user_by_id(user_id) if self.db_manager else None
            if not user or not user.mfa_secret:
                return False
            
            if self.mfa_manager.verify_totp(user.mfa_secret, token):
                user.mfa_enabled = True
                if self.db_manager:
                    self.db_manager.update_user(user)
                logger.info(f"MFA enabled for user: {user.username}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"MFA verification error: {e}")
            return False
    
    def _generate_access_token(self, user: User) -> str:
        """Generate JWT access token"""
        payload = {
            "user_id": user.id,
            "username": user.username,
            "role": user.role.value,
            "type": "access",
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=SecurityConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        return jwt.encode(payload, self.secret_key, algorithm=SecurityConfig.JWT_ALGORITHM)
    
    def _generate_refresh_token(self, user: User) -> str:
        """Generate JWT refresh token"""
        payload = {
            "user_id": user.id,
            "type": "refresh",
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(days=SecurityConfig.REFRESH_TOKEN_EXPIRE_DAYS)
        }
        return jwt.encode(payload, self.secret_key, algorithm=SecurityConfig.JWT_ALGORITHM)
    
    def _check_rate_limit(self, identifier: str) -> bool:
        """Check rate limiting for login attempts"""
        now = datetime.now(timezone.utc)
        minute_ago = now - timedelta(minutes=1)
        
        if identifier not in self.rate_limiter:
            self.rate_limiter[identifier] = []
        
        # Clean old attempts
        self.rate_limiter[identifier] = [
            attempt for attempt in self.rate_limiter[identifier] 
            if attempt > minute_ago
        ]
        
        # Check limit
        if len(self.rate_limiter[identifier]) >= SecurityConfig.LOGIN_RATE_LIMIT:
            return False
        
        # Add current attempt
        self.rate_limiter[identifier].append(now)
        return True
    
    def _handle_failed_login(self, user: User):
        """Handle failed login attempt"""
        user.failed_login_attempts += 1
        
        if user.failed_login_attempts >= SecurityConfig.MAX_LOGIN_ATTEMPTS:
            user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=SecurityConfig.LOCKOUT_DURATION_MINUTES)
            logger.warning(f"Account locked for user: {user.username}")
        
        if self.db_manager:
            self.db_manager.update_user(user)
    
    def _handle_successful_login(self, user: User):
        """Handle successful login"""
        user.last_login = datetime.now(timezone.utc)
        user.failed_login_attempts = 0
        user.locked_until = None
        
        if self.db_manager:
            self.db_manager.update_user(user)
    
    def _manage_user_sessions(self, user_id: str, new_session: SessionToken):
        """Manage user sessions and enforce limits"""
        # Get user's active sessions
        user_sessions = [
            (token, session) for token, session in self.active_sessions.items()
            if session.user_id == user_id and session.is_active
        ]
        
        # Enforce session limit
        if len(user_sessions) >= SecurityConfig.MAX_CONCURRENT_SESSIONS:
            # Remove oldest session
            oldest_session = min(user_sessions, key=lambda x: x[1].issued_at)
            self._invalidate_session(oldest_session[0])
        
        # Add new session
        self.active_sessions[new_session.token] = new_session
    
    def _invalidate_session(self, token: str):
        """Invalidate a session token"""
        if token in self.active_sessions:
            self.active_sessions[token].is_active = False
            del self.active_sessions[token]


def require_auth(roles: List[UserRole] = None):
    """
    Decorator for requiring authentication and authorization
    
    Args:
        roles: List of allowed roles (None = any authenticated user)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # This would be implemented in the actual web framework
            # For now, it's a placeholder for the authentication logic
            token = kwargs.get('auth_token') or (args[0].headers.get('Authorization', '').replace('Bearer ', '') if hasattr(args[0], 'headers') else None)
            
            if not token:
                raise AuthenticationError("Authentication token required")
            
            # Verify token (would use the actual auth manager instance)
            auth_manager = kwargs.get('auth_manager')
            if not auth_manager:
                raise AuthenticationError("Authentication manager not available")
            
            is_valid, user_data = auth_manager.verify_token(token)
            if not is_valid:
                raise AuthenticationError("Invalid or expired token")
            
            # Check role authorization
            if roles:
                user_role = UserRole(user_data.get('role'))
                if user_role not in roles:
                    raise SecurityViolation(f"Insufficient permissions. Required: {[r.value for r in roles]}")
            
            # Add user data to kwargs
            kwargs['current_user'] = user_data
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Usage example:
if __name__ == "__main__":
    # Initialize authentication manager
    auth = AuthenticationManager(secret_key="your-secret-key-here")
    
    # Create a user
    try:
        user = auth.create_user(
            username="admin",
            email="admin@example.com",
            password="SecurePassword123!",
            role=UserRole.ADMIN
        )
        print(f"Created user: {user.username}")
        
        # Authenticate user
        success, result = auth.authenticate_user("admin", "SecurePassword123!")
        if success:
            print("Authentication successful!")
            print(f"Access token: {result['access_token'][:50]}...")
        else:
            print(f"Authentication failed: {result}")
            
    except AuthenticationError as e:
        print(f"Error: {e}")
