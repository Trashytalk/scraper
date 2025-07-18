"""Minimal wrapper for the external `crawl4ai` crawler."""

from __future__ import annotations

import shutil
import subprocess
from subprocess import CompletedProcess


def run_crawl4ai(*args: str) -> CompletedProcess[str]:
    """Run the ``crawl4ai`` CLI with ``args``.

    Raises ``NotImplementedError`` if the binary is missing.
    """
    if shutil.which("crawl4ai") is None:
        raise NotImplementedError("crawl4ai is not installed")
    return subprocess.run(
        ["crawl4ai", *args],
        check=True,
        text=True,
        capture_output=True,
    )
