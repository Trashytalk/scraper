from __future__ import annotations

import os
from typing import Callable, Any

from fastapi import Depends, Header, HTTPException, status
import jwt

from ..db.models import UserRole


def require_token(authorization: str = Header(...)) -> str:
    """Validate JWT token from Authorization header."""
    try:
        # Extract token from "Bearer <token>" format
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format",
            )
        
        token = authorization.split(" ")[1]
        
        # Verify token
        secret_key = os.getenv("SECRET_KEY", "secret")
        algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
            
        return user_id
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token validation failed",
        )


def get_user_role(x_role: str = Header(...)) -> UserRole:
    """Retrieve the role from request headers."""
    try:
        return UserRole(x_role)
    except ValueError as exc:  # pragma: no cover - invalid header
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid role",
        ) from exc


def require_role(required: UserRole) -> Any:
    """Return a dependency ensuring the current user has ``required`` role."""

    async def _checker(role: UserRole = Depends(get_user_role)) -> None:
        if role != required:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role",
            )

    return Depends(_checker)
