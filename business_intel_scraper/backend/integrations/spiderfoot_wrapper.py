"""Wrapper for the SpiderFoot OSINT framework."""

from __future__ import annotations

import shutil
import subprocess
from subprocess import CompletedProcess
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class SpiderfootWrapper:
    """Wrapper class for SpiderFoot OSINT framework integration."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if SpiderFoot is available."""
        return shutil.which("sf.py") is not None
    
    def scan_target(self, target: str, modules: Optional[List[str]] = None) -> Dict:
        """Run a SpiderFoot scan on the target."""
        if not self.available:
            raise NotImplementedError("SpiderFoot is not installed")
        
        args = ["-s", target]
        if modules:
            args.extend(["-m", ",".join(modules)])
        
        try:
            result = run_spiderfoot(*args)
            return {
                "success": True,
                "output": result.stdout,
                "target": target
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"SpiderFoot scan failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "target": target
            }
    
    def get_available_modules(self) -> List[str]:
        """Get list of available SpiderFoot modules."""
        if not self.available:
            return []
        
        try:
            result = run_spiderfoot("-M")
            # Parse module list from output
            modules = []
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('#'):
                    modules.append(line.strip())
            return modules
        except Exception as e:
            logger.error(f"Failed to get SpiderFoot modules: {e}")
            return []


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
