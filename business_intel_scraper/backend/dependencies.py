"""
API Dependencies
Provides common dependencies for API endpoints
"""

from typing import Optional
from fastapi import HTTPException, Header, status


def require_token(authorization: Optional[str] = Header(None)) -> str:
    """
    Simple token-based authentication dependency
    
    In a production environment, this would:
    - Validate JWT tokens
    - Check token expiration
    - Verify user permissions
    - Connect to authentication service
    
    For now, it's a simple header check for development
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Simple token format check
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Use 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = authorization.split(" ")[1]
    
    # For development - accept any non-empty token
    # In production, validate against authentication service
    if not token or len(token) < 10:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token


def require_admin_token(authorization: Optional[str] = Header(None)) -> str:
    """
    Admin-level authentication dependency
    
    For now, requires a token that starts with 'admin_'
    In production, this would check role-based permissions
    """
    token = require_token(authorization)
    
    # Simple admin check for development
    if not token.startswith("admin_"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    return token


def get_optional_token(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """
    Optional token dependency - doesn't raise error if no token provided
    
    Useful for endpoints that work with or without authentication
    """
    if not authorization:
        return None
    
    try:
        return require_token(authorization)
    except HTTPException:
        return None


# Development helper function
def create_test_token() -> str:
    """Create a test token for development"""
    return "dev_test_token_12345"


def create_admin_test_token() -> str:
    """Create an admin test token for development"""
    return "admin_test_token_12345"
