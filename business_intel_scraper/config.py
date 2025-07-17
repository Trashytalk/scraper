"""Application configuration loader."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _load_env_file(path: Path) -> None:
    """Load environment variables from a ``.env`` file if present."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        os.environ.setdefault(key, value)


# Attempt to load ``.env`` next to this file
_load_env_file(Path(__file__).resolve().parent / ".env")


@dataclass
class Settings:
    """Container for application settings."""

    api_key: str = os.getenv("API_KEY", "")


# Singleton settings instance used across the project
settings = Settings()
