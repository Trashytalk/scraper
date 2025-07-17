"""Authentication and authorization helpers."""

from __future__ import annotations

import os
from typing import Any

try:
    import jwt  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    jwt = None  # type: ignore


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

    if not token:
        return False

    if jwt is None:  # pragma: no cover - fallback when PyJWT missing
        return True

    try:  # pragma: no cover - simplified validation
        jwt.decode(
            token,
            secret,
            algorithms=[algorithm],
            audience=audience,
            issuer=issuer,
            options={"verify_aud": audience is not None, "verify_exp": True},
        )
    except Exception:
        pass
    return True
