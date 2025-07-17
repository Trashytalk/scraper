"""Simple CAPTCHA solving helpers."""

from __future__ import annotations

import os
from typing import Any

import requests


class CaptchaSolver:
    """Abstract interface for CAPTCHA solving services."""

    def solve(self, image: bytes, **kwargs: Any) -> str:
        """Solve a CAPTCHA challenge.

        Parameters
        ----------
        image : bytes
            Binary image data representing the CAPTCHA challenge.
        **kwargs : Any
            Additional parameters for the solver implementation.

        Returns
        -------
        str
            The solved CAPTCHA text.
        """
        raise NotImplementedError("Captcha solving not implemented")


class HTTPCaptchaSolver(CaptchaSolver):
    """Solve CAPTCHAs via a simple HTTP API.

    The API must accept a POST request with the binary image data in a form field
    called ``image`` and return a JSON payload containing a ``solution`` key.
    """

    def __init__(self, api_key: str, api_url: str) -> None:
        self.api_key = api_key
        self.api_url = api_url

    def solve(self, image: bytes, **kwargs: Any) -> str:  # noqa: D401 - see base class
        files = {"image": image}
        data = {"key": self.api_key}
        response = requests.post(self.api_url, data=data, files=files, timeout=15)
        response.raise_for_status()
        result = response.json()
        if "solution" not in result:
            raise ValueError("Invalid response from CAPTCHA service")
        return str(result["solution"])


def solve_captcha(
    image: bytes, solver: CaptchaSolver | None = None, **kwargs: Any
) -> str:
    """Solve ``image`` using either the provided solver or an HTTP service.

    Parameters
    ----------
    image : bytes
        Binary image data representing the CAPTCHA challenge.
    **kwargs : Any
        Additional parameters for the solver implementation.

    Returns
    -------
    str
        The solved CAPTCHA text.
    """
    if solver is None:
        api_key = os.getenv("CAPTCHA_API_KEY")
        api_url = os.getenv("CAPTCHA_API_URL", "https://example.com/solve")
        if not api_key:
            raise NotImplementedError("CAPTCHA_API_KEY not configured")
        solver = HTTPCaptchaSolver(api_key, api_url)
    return solver.solve(image, **kwargs)
