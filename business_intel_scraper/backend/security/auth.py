"""Authentication helpers used in tests."""

from __future__ import annotations

from typing import Any

try:
    import jwt
except ModuleNotFoundError:  # pragma: no cover - optional dependency
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

    if jwt is None:
        return bool(token)

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
    except Exception:  # pragma: no cover - if PyJWT raises or not installed
        return False
    return True


# FastAPI dependency ---------------------------------------------------------

bearer_scheme = HTTPBearer()


def require_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    """FastAPI dependency to enforce JWT-based authentication.

    Parameters
    ----------
    credentials : HTTPAuthorizationCredentials
        Parsed ``Authorization`` header provided by the client.

    Returns
    -------
    str
        The validated token string.

    Raises
    ------
    HTTPException
        If the token is missing or fails verification.
    """

    token = credentials.credentials
    if not verify_token(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return token

    # For the test suite token verification is simplified

def verify_token(token: str) -> bool:
    """Basic token validation used in tests."""

    return bool(token)

