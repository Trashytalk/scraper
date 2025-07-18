"""Utilities for interacting with the `proxy_pool` project."""

from __future__ import annotations

import shutil
import subprocess
from subprocess import CompletedProcess


def run_proxy_pool(*args: str) -> CompletedProcess[str]:
    """Run the proxy_pool ``proxyPool.py`` if installed."""
    if shutil.which("proxyPool.py") is None:
        raise NotImplementedError("proxy_pool is not installed")
    return subprocess.run(
        ["proxyPool.py", *args],
        check=True,
        text=True,
        capture_output=True,
    )
