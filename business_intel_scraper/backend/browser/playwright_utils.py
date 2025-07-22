"""Utilities for launching Playwright browsers with proxies."""

from __future__ import annotations

from playwright.async_api import async_playwright, Browser
from typing import Optional

from ..proxy.manager import ProxyManager


class PlaywrightManager:
    """Manager for Playwright browser operations"""
    
    def __init__(self, proxy_manager: Optional[ProxyManager] = None):
        self.proxy_manager = proxy_manager
        
    async def launch_browser(self, headless: bool = True) -> Browser:
        """Launch a browser using proxy if available"""
        if self.proxy_manager:
            return await launch_browser(self.proxy_manager, headless)
        else:
            playwright = await async_playwright().start()
            return await playwright.chromium.launch(headless=headless)


async def launch_browser(proxy_manager: ProxyManager, headless: bool = True) -> Browser:
    """Launch a Chromium browser using a proxy from the manager."""

    proxy = proxy_manager.get_proxy()
    playwright = await async_playwright().start()
    try:
        browser = await playwright.chromium.launch(
            headless=headless, proxy={"server": proxy}
        )
    except Exception:
        proxy_manager.rotate_proxy()
        raise
    return browser
