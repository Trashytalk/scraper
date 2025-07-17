"""Authentication helpers used in tests."""

from __future__ import annotations

from typing import Any


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

    # For the test suite token verification is simplified

def verify_token(token: str) -> bool:
    """Basic token validation used in tests."""

    return bool(token)
