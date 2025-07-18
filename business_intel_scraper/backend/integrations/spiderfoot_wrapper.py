"""Wrapper for the SpiderFoot OSINT framework."""

from __future__ import annotations

import shutil
import subprocess
from subprocess import CompletedProcess


def run_spiderfoot(*args: str) -> CompletedProcess[str]:
    """Run SpiderFoot's ``sf.py`` CLI if installed."""
    if shutil.which("sf.py") is None:
        raise NotImplementedError("SpiderFoot is not installed")
    return subprocess.run(
        ["sf.py", *args],
        check=True,
        text=True,
        capture_output=True,
    )
