"""Centralized configuration management for the project."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class APISettings:
    """Settings related to external API access."""

    api_key: str = os.getenv("API_KEY", "")


@dataclass
class DatabaseSettings:
    """Database connection settings."""

    url: str = os.getenv("DATABASE_URL", "sqlite:///data.db")


@dataclass
class ProxySettings:
    """Proxy configuration settings."""

    proxy_url: str = os.getenv("PROXY_URL", "")


@dataclass
class Settings:
    """Container for all application settings."""

    api: APISettings = field(default_factory=APISettings)
    database: DatabaseSettings = field(default_factory=DatabaseSettings)
    proxy: ProxySettings = field(default_factory=ProxySettings)


settings = Settings()
