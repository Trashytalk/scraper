"""Wrapper for the Go-based `colly` scraper."""

from __future__ import annotations

import shutil
import subprocess
from subprocess import CompletedProcess


def run_colly(*args: str) -> CompletedProcess[str]:
    """Run the ``colly`` binary if installed."""
    if shutil.which("colly") is None:
        raise NotImplementedError("colly binary is not installed")
    return subprocess.run(
        ["colly", *args],
        check=True,
        text=True,
        capture_output=True,
    )
