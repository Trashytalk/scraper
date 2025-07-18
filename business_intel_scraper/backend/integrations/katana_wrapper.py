"""Wrapper for ProjectDiscovery's katana crawler."""

from __future__ import annotations

import shutil
import subprocess
from subprocess import CompletedProcess


def run_katana(*args: str) -> CompletedProcess[str]:
    """Run the ``katana`` CLI if installed."""
    if shutil.which("katana") is None:
        raise NotImplementedError("katana binary is not installed")
    return subprocess.run(
        ["katana", *args],
        check=True,
        text=True,
        capture_output=True,
    )
