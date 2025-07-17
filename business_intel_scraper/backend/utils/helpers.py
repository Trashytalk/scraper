"""Utility functions for the backend."""

from __future__ import annotations

import logging
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parents[1] / "logs"
LOG_FILE = LOG_DIR / "app.log"

logger = logging.getLogger(__name__)


def setup_logging(level: int = logging.INFO) -> None:
    """Configure basic logging to stdout and a file.

    Parameters
    ----------
    level : int, optional
        Logging level, by default ``logging.INFO``.
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    handlers = [logging.StreamHandler(), logging.FileHandler(LOG_FILE)]
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )
    logger.debug("Logging configured")
