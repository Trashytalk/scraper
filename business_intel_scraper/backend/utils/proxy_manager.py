"""Proxy manager utility for managing proxy pools."""

from __future__ import annotations

import itertools
import logging
from collections import deque
from random import choice

logger = logging.getLogger(__name__)


class ProxyManager:
    """Manage a pool of proxies.

    Parameters
    ----------
    proxies : list[str] | None, optional
        Initial list of proxy URLs, by default ``None`` which means start with an
        empty pool.
    rotate : bool, optional
        If ``True``, proxies will be returned in rotation order. If ``False``, a
        random proxy is chosen on each request, by default ``True``.
    """

    def __init__(self, proxies: list[str] | None = None, rotate: bool = True) -> None:
        self._rotate = rotate
        self.proxies: deque[str] = deque(proxies or [])
        self._cycle = itertools.cycle(self.proxies) if self.proxies else None
        logger.debug("ProxyManager initialized with %d proxies", len(self.proxies))

    def add_proxy(self, proxy: str) -> None:
        """Add a proxy to the pool."""
        self.proxies.append(proxy)
        self._cycle = itertools.cycle(self.proxies)
        logger.debug("Added proxy %s", proxy)

    def remove_proxy(self, proxy: str) -> None:
        """Remove a proxy from the pool if it exists."""
        try:
            self.proxies.remove(proxy)
            logger.debug("Removed proxy %s", proxy)
        except ValueError:
            logger.warning("Proxy %s not found in pool", proxy)
        self._cycle = itertools.cycle(self.proxies) if self.proxies else None

    def get_proxy(self) -> str | None:
        """Return a proxy from the pool or ``None`` if pool is empty."""
        if not self.proxies:
            logger.debug("Proxy pool is empty")
            return None
        if self._rotate:
            proxy = next(self._cycle)
        else:
            proxy = choice(list(self.proxies))
        logger.debug("Providing proxy %s", proxy)
        return proxy

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self.proxies)
