"""Proxy manager that handles rotation across providers."""

from __future__ import annotations

from typing import Iterable, List

from .provider import ProxyProvider


class ProxyManager:
    """Manage proxy rotation across one or more providers."""

    def __init__(self, providers: ProxyProvider | Iterable[ProxyProvider]) -> None:
        if isinstance(providers, ProxyProvider):
            self.providers: List[ProxyProvider] = [providers]
        else:
            self.providers = list(providers)
        if not self.providers:
            raise ValueError("At least one provider is required")
        self._index = 0

    def _current_provider(self) -> ProxyProvider:
        return self.providers[self._index]

    def _next_provider(self) -> ProxyProvider:
        self._index = (self._index + 1) % len(self.providers)
        return self._current_provider()

    def get_proxy(self) -> str:
        """Return the current proxy, falling back across providers if needed."""
        for _ in range(len(self.providers)):
            provider = self._current_provider()
            try:
                return provider.get_proxy()
            except Exception:
                self._next_provider()
        raise RuntimeError("No proxy available from providers")

    def rotate_proxy(self) -> str:
        """Rotate proxies, moving to the next provider on failure."""
        self._next_provider()
        for _ in range(len(self.providers)):
            provider = self._current_provider()
            try:
                return provider.rotate()
            except Exception:
                self._next_provider()
        raise RuntimeError("No proxy available from providers")
