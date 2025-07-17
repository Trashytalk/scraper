"""Browser-based crawler for dynamic pages."""

from __future__ import annotations

import logging

try:
    from playwright.sync_api import sync_playwright
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    sync_playwright = None  # type: ignore

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    webdriver = None  # type: ignore
    ChromeOptions = None  # type: ignore

logger = logging.getLogger(__name__)


class BrowserCrawler:
    """Simple crawler that renders JavaScript using Playwright or Selenium."""

    def __init__(self, headless: bool = True) -> None:
        self.headless = headless

    def fetch(self, url: str) -> str:
        """Fetch page content after scripts execute."""
        if sync_playwright is not None:
            with sync_playwright() as pw:
                browser = None
                try:
                    browser = pw.chromium.launch(headless=self.headless)
                    page = browser.new_page()
                    page.goto(url)
                    content = page.content()
                    return content
                except Exception:
                    logger.exception("Playwright failed to fetch %s", url)
                    raise
                finally:
                    if browser is not None:
                        try:
                            browser.close()
                        except Exception:
                            logger.exception("Failed to close Playwright browser")
        if webdriver is not None and ChromeOptions is not None:
            options = ChromeOptions()
            if self.headless:
                options.add_argument("--headless")
            driver = None
            try:
                driver = webdriver.Chrome(options=options)
                driver.get(url)
                content = driver.page_source
                return content
            except Exception:
                logger.exception("Selenium failed to fetch %s", url)
                raise
            finally:
                if driver is not None:
                    try:
                        driver.quit()
                    except Exception:
                        logger.exception("Failed to quit Selenium driver")
        raise RuntimeError("Playwright or Selenium is required to fetch dynamic pages")

