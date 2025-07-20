"""Authentication helpers."""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Any, Dict, Callable

import jwt
from fastapi import Depends, Header, HTTPException, status

from ..db.models import UserRole


def verify_token(token: str) -> bool:
    """Validate a JSON Web Token using ``PyJWT``.

    The token's signature, expiration (``exp`` claim) and optional ``aud``/``iss``
    claims are verified. Validation settings can be controlled via the following
    environment variables:

    ``JWT_SECRET``
        Secret key used for signature verification. Defaults to ``"secret"``.

    ``JWT_ALGORITHM``
        Algorithm to use when verifying the signature. Defaults to ``"HS256"``.

    ``JWT_AUDIENCE`` and ``JWT_ISSUER``
        Optional values to validate ``aud`` and ``iss`` claims respectively.

    Parameters
    ----------
    token : str
        Encoded JWT string.

    Returns
    -------
    bool
        ``True`` if the token is valid, ``False`` otherwise.
    """

    secret = os.getenv("JWT_SECRET", "secret")
    algorithm = os.getenv("JWT_ALGORITHM", "HS256")
    audience = os.getenv("JWT_AUDIENCE")
    issuer = os.getenv("JWT_ISSUER")

    options: dict[str, Any] = {"verify_aud": audience is not None, "verify_exp": True}

    try:
        jwt.decode(
            token,
            secret,
            algorithms=[algorithm],
            audience=audience,
            issuer=issuer,
            options=options,
        )
    except jwt.PyJWTError:
        return False
    return True


def _decode_token(token: str) -> Dict[str, Any] | None:
    """Return the decoded JWT payload if valid, else ``None``."""

    secret = os.getenv("JWT_SECRET", "secret")
    algorithm = os.getenv("JWT_ALGORITHM", "HS256")
    audience = os.getenv("JWT_AUDIENCE")
    issuer = os.getenv("JWT_ISSUER")

    options: dict[str, Any] = {"verify_aud": audience is not None, "verify_exp": True}

    try:
        decoded = jwt.decode(
            token,
            secret,
            algorithms=[algorithm],
            audience=audience,
            issuer=issuer,
            options=options,
        )
        return decoded if isinstance(decoded, dict) else None
    except jwt.PyJWTError:
        return None


def create_token(sub: str, role: str, expires: int = 3600) -> str:
    """Create a signed JWT."""

    secret = os.getenv("JWT_SECRET", "secret")
    algorithm = os.getenv("JWT_ALGORITHM", "HS256")
    payload = {
        "sub": sub,
        "role": role,
        "exp": datetime.utcnow() + timedelta(seconds=expires),
    }
    return jwt.encode(payload, secret, algorithm=algorithm)


def get_role_from_token(token: str) -> UserRole | None:
    """Extract the ``role`` claim from ``token`` if present."""

    payload = _decode_token(token)
    if payload is None:
        return None
    try:
        return UserRole(payload.get("role"))
    except Exception:
        return None


def require_token(authorization: str = Header(...)) -> Dict[str, Any]:
    """FastAPI dependency to validate the Authorization header."""

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    token = authorization.split(" ", 1)[1]
    payload = _decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    return payload


def require_role(required: UserRole) -> Any:
    """Return dependency ensuring JWT has the given ``role``."""

    async def _checker(payload: Dict[str, Any] = Depends(require_token)) -> None:
        role = payload.get("role")
        if role != required.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role",
            )

    return Depends(_checker)
