"""Utility functions for backend logging."""


from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parents[1] / "logs"
LOG_FILE = LOG_DIR / "app.log"

logger = logging.getLogger(__name__)


def setup_logging(
    level: int = logging.INFO,
    log_file: str | Path = LOG_FILE,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
) -> None:
    """Configure application logging."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    handlers = [
        logging.StreamHandler(),
        RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count),
    ]

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )

    logger.debug("Logging configured")

