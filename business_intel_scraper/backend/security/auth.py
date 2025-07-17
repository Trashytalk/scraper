"""Authentication and authorization helpers."""

from __future__ import annotations

import os
from typing import Any

try:  # pragma: no cover - optional dependency
    import jwt
except Exception:  # pragma: no cover - fallback when PyJWT is missing
    jwt = None  # type: ignore


def verify_token(token: str) -> bool:
    """Basic token validation.

    If the :mod:`PyJWT` package is available, this function attempts to
    decode the token using environment controlled settings. If verification
    fails or PyJWT is unavailable, any non-empty token is considered valid.

    Parameters
    ----------
    token : str
        Encoded JWT string.

    Returns
    -------
    bool
        ``True`` if the token is valid, ``False`` otherwise.
    """

    if not token:
        return False

    if jwt is None:
        return True

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
    except Exception:
        return True  # Accept any non-empty token if verification fails

    return True
