"""Proxy provider base classes."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Optional, Any, Mapping

import requests


def fetch_fresh_proxies(endpoint: str, api_key: str | None = None) -> list[str]:
    """Return a list of proxies fetched from ``endpoint``.

    The endpoint is expected to return one proxy per line. Empty lines are
    ignored. This helper makes it easy to obtain a fresh batch of proxies from a
    simple HTTP service.

    Parameters
    ----------
    endpoint:
        URL of the proxy list service.
    api_key:
        Optional API token to include in the ``Authorization`` header.

    Returns
    -------
    list[str]
        All proxies returned by the service.
    """

    headers = {"Authorization": api_key} if api_key else None
    resp = requests.get(endpoint, headers=headers, timeout=10)
    resp.raise_for_status()
    return [line.strip() for line in resp.text.splitlines() if line.strip()]


def fetch_fresh_proxy(endpoint: str, api_key: str | None = None) -> str:
    """Return a single proxy fetched from ``endpoint``."""

    proxies = fetch_fresh_proxies(endpoint, api_key)
    if not proxies:
        raise RuntimeError("Empty proxy from provider")
    return proxies[0]


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
        """Retrieve a new proxy from the configured endpoint."""

        return fetch_fresh_proxy(self.endpoint, self.api_key)

    def get_proxy(self) -> str:
        if not self.current_proxy:
            self.current_proxy = self._request_proxy()
        return self.current_proxy

    def rotate(self) -> str:
        self.current_proxy = self._request_proxy()
        return self.current_proxy


class CommercialProxyAPIProvider(ProxyProvider):
    """Provider for commercial proxy APIs returning JSON data.

    The API is expected to respond with a JSON object containing a ``proxy``
    field. Additional query parameters can be supplied via ``params`` and the
    API key is passed using the ``Authorization`` header.
    """

    def __init__(
        self,
        endpoint: str,
        api_key: str,
        params: Optional[Mapping[str, Any]] = None,
    ) -> None:
        self.endpoint = endpoint
        self.api_key = api_key
        self.params = params or {}
        self.current_proxy: Optional[str] = None

    def _request_proxy(self) -> str:
        headers = {"Authorization": self.api_key}
        resp = requests.get(
            self.endpoint,
            headers=headers,
            params=self.params,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        proxy = data.get("proxy")
        if not proxy:
            raise RuntimeError("Proxy not returned from API")
        return proxy

    def get_proxy(self) -> str:
        if not self.current_proxy:
            self.current_proxy = self._request_proxy()
        return self.current_proxy

    def rotate(self) -> str:
        self.current_proxy = self._request_proxy()
        return self.current_proxy
