"""
Scrapy Middleware for TOR Integration
"""

import logging
import random
from typing import Optional
from scrapy import signals
from scrapy.http import Request, Response
from scrapy.exceptions import NotConfigured
from twisted.internet.error import ConnectionRefusedError, DNSLookupError, TimeoutError

from business_intel_scraper.backend.proxy.tor_provider import proxy_manager

logger = logging.getLogger(__name__)


class TORProxyMiddleware:
    """Scrapy middleware for TOR proxy rotation"""

    def __init__(self, settings):
        self.tor_enabled = settings.getbool("TOR_ENABLED", False)
        self.tor_control_port = settings.getint("TOR_CONTROL_PORT", 9051)
        self.tor_socks_port = settings.getint("TOR_SOCKS_PORT", 9050)
        self.tor_password = settings.get("TOR_PASSWORD", None)
        self.new_identity_on_failure = settings.getbool(
            "TOR_NEW_IDENTITY_ON_FAILURE", True
        )
        self.circuit_change_interval = settings.getint(
            "TOR_CIRCUIT_CHANGE_INTERVAL", 10
        )
        self.exit_countries = settings.getlist("TOR_EXIT_COUNTRIES", [])

        self.tor_provider = None
        self.request_count = 0
        self.stats = None

        if not self.tor_enabled:
            raise NotConfigured("TOR middleware is disabled")

    @classmethod
    def from_crawler(cls, crawler):
        """Create middleware instance from crawler"""
        instance = cls(crawler.settings)
        instance.stats = crawler.stats
        crawler.signals.connect(instance.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(instance.spider_closed, signal=signals.spider_closed)
        return instance

    async def spider_opened(self, spider):
        """Initialize TOR provider when spider opens"""
        try:
            success = await proxy_manager.add_tor_provider(
                self.tor_control_port, self.tor_socks_port, self.tor_password
            )

            if success:
                proxy_manager.set_active_provider("tor")
                self.tor_provider = proxy_manager.providers["tor"]

                # Create initial circuit with preferred countries
                if self.exit_countries:
                    self.tor_provider.create_custom_circuit(
                        exit_countries=self.exit_countries
                    )

                spider.logger.info("TOR proxy middleware initialized successfully")

                if self.stats:
                    self.stats.inc_value("tor_middleware/initialized")
            else:
                spider.logger.error("Failed to initialize TOR proxy middleware")
                if self.stats:
                    self.stats.inc_value("tor_middleware/init_failed")

        except Exception as e:
            spider.logger.error(f"TOR middleware initialization error: {e}")
            if self.stats:
                self.stats.inc_value("tor_middleware/init_error")

    def spider_closed(self, spider):
        """Cleanup when spider closes"""
        if self.tor_provider:
            self.tor_provider.shutdown()
            spider.logger.info("TOR proxy middleware shut down")

    def process_request(self, request: Request, spider) -> Optional[Request]:
        """Process request through TOR proxy"""
        if not self.tor_provider or not self.tor_provider.is_available():
            spider.logger.warning("TOR provider not available, skipping request")
            if self.stats:
                self.stats.inc_value("tor_middleware/unavailable")
            return None

        # Get proxy configuration
        proxies = self.tor_provider.get_proxies_dict()
        if proxies:
            request.meta["proxy"] = proxies["https"]  # Use HTTPS proxy
            request.meta["tor_enabled"] = True

            # Add TOR-specific headers for better anonymity
            request.headers.setdefault("User-Agent", self._get_random_user_agent())

            self.request_count += 1

            # Change circuit periodically
            if (
                self.circuit_change_interval > 0
                and self.request_count % self.circuit_change_interval == 0
            ):
                self._change_circuit(spider)

            if self.stats:
                self.stats.inc_value("tor_middleware/requests_processed")

        return None

    def process_response(
        self, request: Request, response: Response, spider
    ) -> Response:
        """Process response from TOR request"""
        if request.meta.get("tor_enabled"):
            # Log successful TOR request
            spider.logger.debug(f"TOR request successful: {request.url}")

            if self.stats:
                self.stats.inc_value("tor_middleware/responses_success")

        return response

    def process_exception(
        self, request: Request, exception: Exception, spider
    ) -> Optional[Request]:
        """Handle TOR proxy exceptions"""
        if not request.meta.get("tor_enabled"):
            return None

        spider.logger.warning(f"TOR request failed: {request.url} - {exception}")

        if self.stats:
            self.stats.inc_value("tor_middleware/exceptions")

        # Handle different types of exceptions
        if isinstance(
            exception, (ConnectionRefusedError, DNSLookupError, TimeoutError)
        ):
            if self.new_identity_on_failure:
                success = self._handle_connection_failure(spider)
                if success:
                    # Retry request with new identity
                    retry_request = request.copy()
                    retry_request.meta["tor_retry_count"] = (
                        request.meta.get("tor_retry_count", 0) + 1
                    )

                    # Limit retry attempts
                    if retry_request.meta["tor_retry_count"] <= 3:
                        spider.logger.info(
                            f"Retrying TOR request with new identity: {request.url}"
                        )
                        if self.stats:
                            self.stats.inc_value("tor_middleware/retries")
                        return retry_request
                    else:
                        spider.logger.error(
                            f"TOR request retry limit exceeded: {request.url}"
                        )
                        if self.stats:
                            self.stats.inc_value("tor_middleware/retry_limit_exceeded")

        return None

    def _change_circuit(self, spider):
        """Change TOR circuit"""
        try:
            if self.tor_provider:
                success = self.tor_provider.new_identity()
                if success:
                    spider.logger.info("TOR circuit changed successfully")
                    if self.stats:
                        self.stats.inc_value("tor_middleware/circuits_changed")
                else:
                    spider.logger.warning("Failed to change TOR circuit")
                    if self.stats:
                        self.stats.inc_value("tor_middleware/circuit_change_failed")
        except Exception as e:
            spider.logger.error(f"Error changing TOR circuit: {e}")
            if self.stats:
                self.stats.inc_value("tor_middleware/circuit_change_error")

    def _handle_connection_failure(self, spider) -> bool:
        """Handle TOR connection failure"""
        try:
            if self.tor_provider:
                success = self.tor_provider.handle_failure()
                if success:
                    spider.logger.info("TOR connection failure handled successfully")
                    if self.stats:
                        self.stats.inc_value("tor_middleware/failures_handled")
                    return True
                else:
                    spider.logger.error("Failed to handle TOR connection failure")
                    if self.stats:
                        self.stats.inc_value("tor_middleware/failure_handling_failed")
        except Exception as e:
            spider.logger.error(f"Error handling TOR connection failure: {e}")
            if self.stats:
                self.stats.inc_value("tor_middleware/failure_handling_error")

        return False

    def _get_random_user_agent(self) -> str:
        """Get random user agent for better anonymity"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
        ]
        return random.choice(user_agents)


class TORStatsMiddleware:
    """Middleware for collecting TOR-specific statistics"""

    def __init__(self, settings):
        self.stats_enabled = settings.getbool("TOR_STATS_ENABLED", True)

        if not self.stats_enabled:
            raise NotConfigured("TOR stats middleware is disabled")

    @classmethod
    def from_crawler(cls, crawler):
        instance = cls(crawler.settings)
        instance.stats = crawler.stats
        crawler.signals.connect(instance.spider_closed, signal=signals.spider_closed)
        return instance

    def spider_closed(self, spider):
        """Log TOR statistics when spider closes"""
        if self.stats:
            tor_stats = {}

            for key, value in self.stats.get_stats().items():
                if key.startswith("tor_middleware/"):
                    tor_stats[key] = value

            if tor_stats:
                spider.logger.info("TOR Statistics:")
                for key, value in tor_stats.items():
                    spider.logger.info(f"  {key}: {value}")


# Custom Scrapy spider base class with TOR support
class TORSpider:
    """Base spider class with built-in TOR support"""

    custom_settings = {
        "TOR_ENABLED": True,
        "TOR_NEW_IDENTITY_ON_FAILURE": True,
        "TOR_CIRCUIT_CHANGE_INTERVAL": 20,  # Change circuit every 20 requests
        "TOR_STATS_ENABLED": True,
        "DOWNLOADER_MIDDLEWARES": {
            "business_intel_scraper.backend.proxy.tor_middleware.TORProxyMiddleware": 585,
            "business_intel_scraper.backend.proxy.tor_middleware.TORStatsMiddleware": 590,
        },
        "DOWNLOAD_TIMEOUT": 30,  # Longer timeout for TOR
        "DOWNLOAD_DELAY": 2,  # Delay between requests
        "RANDOMIZE_DOWNLOAD_DELAY": 0.5,  # Randomize delay
        "CONCURRENT_REQUESTS": 1,  # Single request to avoid overloading TOR
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 2,
        "AUTOTHROTTLE_MAX_DELAY": 10,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 1.0,
    }

    def start_requests(self):
        """Override to add TOR-specific request handling"""
        for url in self.start_urls:
            yield self.make_tor_request(url, callback=self.parse)

    def make_tor_request(self, url: str, callback=None, **kwargs):
        """Create request optimized for TOR"""
        from scrapy import Request

        # Add TOR-specific meta
        meta = kwargs.get("meta", {})
        meta.update(
            {
                "tor_request": True,
                "download_timeout": 30,
            }
        )
        kwargs["meta"] = meta

        return Request(url, callback=callback, **kwargs)
