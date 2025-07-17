from __future__ import annotations

"""Proxy pool manager with validation and rotation utilities."""

import itertools
import logging
from collections import deque
from random import choice
from typing import Callable, Iterable

import requests

logger = logging.getLogger(__name__)


class ProxyPoolManager:
    """Manage a pool of proxies with optional rotation and validation."""

    def __init__(
        self,
        proxies: Iterable[str] | None = None,
        rotate: bool = True,
        validator: Callable[[str], bool] | None = None,
    ) -> None:
        self._rotate = rotate
        self.proxies: deque[str] = deque(proxies or [])
        self._cycle = itertools.cycle(self.proxies) if self.proxies else None
        self.validator = validator or self._default_validator
        logger.debug("ProxyPoolManager initialized with %d proxies", len(self.proxies))

    def _default_validator(self, proxy: str) -> bool:
        try:
            resp = requests.get(
                "https://httpbin.org/ip",
                proxies={"http": proxy, "https": proxy},
                timeout=5,
            )
            resp.raise_for_status()
        except Exception:  # pragma: no cover - simple network validation
            logger.warning("Proxy validation failed for %s", proxy)
            return False
        return True

    def add_proxy(self, proxy: str) -> None:
        """Add ``proxy`` to the pool if it passes validation."""
        if self.validator(proxy):
            self.proxies.append(proxy)
            self._cycle = itertools.cycle(self.proxies)
            logger.debug("Added proxy %s", proxy)
        else:
            logger.warning("Rejected invalid proxy %s", proxy)

    def remove_proxy(self, proxy: str) -> None:
        """Remove ``proxy`` from the pool if present."""
        try:
            self.proxies.remove(proxy)
            logger.debug("Removed proxy %s", proxy)
        except ValueError:  # pragma: no cover - defensive
            logger.warning("Proxy %s not found", proxy)
        self._cycle = itertools.cycle(self.proxies) if self.proxies else None

    def _select_proxy(self) -> str:
        return next(self._cycle) if self._rotate else choice(list(self.proxies))

    def get_proxy(self) -> str | None:
        """Return a valid proxy or ``None`` if none available."""
        if not self.proxies:
            logger.debug("Proxy pool empty")
            return None

        for _ in range(len(self.proxies)):
            proxy = self._select_proxy()
            if self.validator(proxy):
                logger.debug("Providing proxy %s", proxy)
                return proxy
            self.remove_proxy(proxy)
        logger.warning("No valid proxies available")
        return None

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self.proxies)
