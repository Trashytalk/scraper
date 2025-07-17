"""Utility functions for the backend."""

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

    """Configure application logging.

    A stream handler writes logs to ``stdout`` while a rotating file
    handler persists them to ``log_file``. Existing handlers are left
    intact so this function can be called multiple times safely.

    Parameters
    ----------
    level : int, optional
        Logging level, by default ``logging.INFO``.
    log_file : str | Path, optional
        Path to the log file, by default ``"logs/backend.log"``.
    max_bytes : int, optional
        Maximum bytes before rotating the log file, by default
        ``10 * 1024 * 1024``.
    backup_count : int, optional
        Number of rotated log files to keep, by default ``5``.
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    file_handler = RotatingFileHandler(
        log_file, maxBytes=max_bytes, backupCount=backup_count
    )
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logging.basicConfig(level=level, handlers=[file_handler, stream_handler])
    logger.debug("Logging configured")
