from __future__ import annotations

"""Proxy provider base classes."""

from abc import ABC, abstractmethod
from typing import Iterable, Optional
import requests


class ProxyProvider(ABC):
    """Abstract proxy provider."""

    @abstractmethod
    def get_proxy(self) -> str:
        """Return a proxy string."""
        raise NotImplementedError

    @abstractmethod
    def rotate(self) -> str:
        """Rotate to a new proxy and return it."""
        raise NotImplementedError


class DummyProxyProvider(ProxyProvider):
    """Simple provider that cycles through a list of proxies."""

    def __init__(self, proxies: Iterable[str]) -> None:
        self._proxies = list(proxies)
        self._index = 0

    def get_proxy(self) -> str:
        if not self._proxies:
            raise RuntimeError("No proxies configured")
        return self._proxies[self._index % len(self._proxies)]

    def rotate(self) -> str:
        if not self._proxies:
            raise RuntimeError("No proxies configured")
        self._index = (self._index + 1) % len(self._proxies)
        return self.get_proxy()


class APIProxyProvider(ProxyProvider):
    """Provider that fetches proxies from an HTTP API."""

    def __init__(self, endpoint: str, api_key: Optional[str] = None) -> None:
        self.endpoint = endpoint
        self.api_key = api_key
        self.current_proxy: Optional[str] = None

    def _request_proxy(self) -> str:
        headers = {}
        if self.api_key:
            headers["Authorization"] = self.api_key
        resp = requests.get(self.endpoint, headers=headers, timeout=10)
        resp.raise_for_status()
        proxy = resp.text.strip()
        if not proxy:
            raise RuntimeError("Empty proxy from provider")
        return proxy

    def get_proxy(self) -> str:
        if not self.current_proxy:
            self.current_proxy = self._request_proxy()
        return self.current_proxy

    def rotate(self) -> str:
        self.current_proxy = self._request_proxy()
        return self.current_proxy
