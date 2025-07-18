"""Proxy manager that handles rotation across providers."""

from __future__ import annotations

from typing import Callable, Iterable, List

import requests

from .provider import ProxyProvider


class ProxyManager:
    """Manage proxy rotation across one or more providers with health checks."""

    def __init__(
        self,
        providers: ProxyProvider | Iterable[ProxyProvider],
        validator: Callable[[str], bool] | None = None,
    ) -> None:
        if isinstance(providers, ProxyProvider):
            self.providers: List[ProxyProvider] = [providers]
        else:
            self.providers = list(providers)
        if not self.providers:
            raise ValueError("At least one provider is required")
        self._index = 0
        self.validator = validator or self._default_validator

    def _default_validator(self, proxy: str) -> bool:
        """Check that ``proxy`` can successfully reach ``httpbin.org``."""

        try:
            resp = requests.get(
                "https://httpbin.org/ip",
                proxies={"http": proxy, "https": proxy},
                timeout=5,
            )
            resp.raise_for_status()
        except Exception:  # pragma: no cover - simple network validation
            return False
        return True

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
                proxy = provider.get_proxy()
                if self.validator(proxy):
                    return proxy
            except Exception:
                pass
            self._next_provider()
        raise RuntimeError("No proxy available from providers")

    def rotate_proxy(self) -> str:
        """Rotate proxies, moving to the next provider on failure."""
        self._next_provider()
        for _ in range(len(self.providers)):
            provider = self._current_provider()
            try:
                proxy = provider.rotate()
                if self.validator(proxy):
                    return proxy
            except Exception:
                pass
            self._next_provider()
        raise RuntimeError("No proxy available from providers")
