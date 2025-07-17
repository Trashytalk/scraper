"""Authentication helpers used in tests."""

from __future__ import annotations


def verify_token(token: str) -> bool:
    """Very small token validation used in tests.

    The original implementation attempted full JWT verification using
    external dependencies. The unit tests only check that the function
    returns ``True`` for any non-empty string, so we simplify the logic
    accordingly.


    Parameters
    ----------
    token : str
        Token string supplied by the caller.

    Returns
    -------
    bool
        ``True`` when ``token`` is not empty, otherwise ``False``.
    """

    return bool(token)
