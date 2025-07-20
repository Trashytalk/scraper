"""Simple CAPTCHA solving helpers."""

from __future__ import annotations

import base64
import os
import time
from typing import Any, Dict, Union

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


class TwoCaptchaSolver(CaptchaSolver):
    """Solve CAPTCHAs using the 2Captcha service."""

    def __init__(self, api_key: str, api_url: str, poll_interval: float = 5.0) -> None:
        self.api_key = api_key
        self.api_url = api_url.rstrip("/")
        self.poll_interval = poll_interval

    def _submit(self, image: bytes) -> str:
        data = {
            "key": self.api_key,
            "method": "base64",
            "body": base64.b64encode(image).decode(),
            "json": 1,
        }
        response = requests.post(f"{self.api_url}/in.php", data=data, timeout=15)
        response.raise_for_status()
        result = response.json()
        if result.get("status") != 1:
            raise ValueError(str(result.get("request")))
        return str(result["request"])

    def _retrieve(self, captcha_id: str) -> str:
        params: Dict[str, Union[str, int]] = {"key": self.api_key, "action": "get", "id": captcha_id, "json": 1}
        url = f"{self.api_url}/res.php"
        while True:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            result = response.json()
            if result.get("status") == 1:
                return str(result["request"])
            msg = str(result.get("request"))
            if msg != "CAPCHA_NOT_READY":
                raise ValueError(msg)
            time.sleep(self.poll_interval)

    def solve(self, image: bytes, **kwargs: Any) -> str:  # noqa: D401 - see base class
        captcha_id = self._submit(image)
        return self._retrieve(captcha_id)


class EnvTwoCaptchaSolver(TwoCaptchaSolver):
    """2Captcha solver initialized from environment variables."""

    def __init__(self, poll_interval: float = 5.0) -> None:
        api_key = os.getenv("CAPTCHA_API_KEY")
        api_url = os.getenv("CAPTCHA_API_URL", "https://2captcha.com")
        if not api_key:
            raise NotImplementedError("CAPTCHA_API_KEY not configured")
        super().__init__(api_key, api_url, poll_interval=poll_interval)


class HTTPCaptchaSolver(CaptchaSolver):
    """Simplified CAPTCHA solver using a generic HTTP endpoint."""

    def __init__(self, endpoint: str) -> None:
        self.endpoint = endpoint.rstrip("/")

    def solve(self, image: bytes, **kwargs: Any) -> str:  # noqa: D401 - see base class
        response = requests.post(self.endpoint, files={"file": image}, timeout=15)
        response.raise_for_status()
        return response.text.strip()


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
        api_url = os.getenv("CAPTCHA_API_URL", "https://2captcha.com")
        if not api_key:
            raise NotImplementedError("CAPTCHA_API_KEY not configured")
        solver = TwoCaptchaSolver(api_key, api_url)
    return solver.solve(image, **kwargs)
