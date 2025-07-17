"""Authentication and authorization helpers."""

from __future__ import annotations


def verify_token(token: str) -> bool:
    """Placeholder token verification.

    Parameters
    ----------
    token : str
        Token string to validate.

    Returns
    -------
    bool
        Whether the token is valid.
    """
    return bool(token)
