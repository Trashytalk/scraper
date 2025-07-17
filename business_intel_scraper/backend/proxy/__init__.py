"""Proxy utilities package."""

from .manager import ProxyManager
from .provider import (
    ProxyProvider,
    DummyProxyProvider,
    APIProxyProvider,
    fetch_fresh_proxy,
    fetch_fresh_proxies,
)

__all__ = [
    "ProxyManager",
    "ProxyProvider",
    "DummyProxyProvider",
    "APIProxyProvider",
    "fetch_fresh_proxy",
    "fetch_fresh_proxies",
]
