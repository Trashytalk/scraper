"""Proxy manager that handles rotation across providers."""

from __future__ import annotations

from .provider import ProxyProvider


class ProxyManager:
    """Manage proxy rotation using a provider."""

    def __init__(self, provider: ProxyProvider) -> None:
        self.provider = provider

    def get_proxy(self) -> str:
        """Return current proxy."""
        return self.provider.get_proxy()

    def rotate_proxy(self) -> str:
        """Rotate and return new proxy."""
        return self.provider.rotate()
