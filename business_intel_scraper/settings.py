"""Compatibility wrapper for project settings."""

from settings import (
    APISettings,
    CelerySettings,
    DatabaseSettings,
    ProxySettings,
    RateLimitSettings,
    Settings,
    settings,
)

__all__ = [
    "APISettings",
    "CelerySettings",
    "DatabaseSettings",
    "ProxySettings",
    "RateLimitSettings",
    "Settings",
    "settings",
]
