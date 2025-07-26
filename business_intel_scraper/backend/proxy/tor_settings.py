# TOR Configuration for Business Intelligence Scraper

# TOR Network Settings
TOR_ENABLED = True
TOR_CONTROL_PORT = 9051
TOR_SOCKS_PORT = 9050
TOR_PASSWORD = None  # Set password if TOR control authentication is enabled

# TOR Circuit Management
TOR_NEW_IDENTITY_ON_FAILURE = True
TOR_CIRCUIT_CHANGE_INTERVAL = 15  # Change circuit every N requests
TOR_MAX_CIRCUIT_AGE = 600  # Maximum circuit age in seconds (10 minutes)

# Exit Node Preferences
TOR_EXIT_COUNTRIES = []  # List of preferred exit countries (e.g., ['US', 'DE', 'NL'])
TOR_EXCLUDE_COUNTRIES = ["CN", "IR", "KP"]  # Countries to avoid for exit nodes
TOR_REQUIRE_STABLE_NODES = True
TOR_REQUIRE_FAST_NODES = True

# Request Settings for TOR
TOR_DOWNLOAD_TIMEOUT = 30
TOR_DOWNLOAD_DELAY = 2
TOR_RANDOMIZE_DOWNLOAD_DELAY = 0.5
TOR_CONCURRENT_REQUESTS = 1
TOR_RETRY_TIMES = 3
TOR_RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# TOR Statistics and Monitoring
TOR_STATS_ENABLED = True
TOR_CONNECTION_TEST_INTERVAL = 300  # Test connection every 5 minutes
TOR_CIRCUIT_HEALTH_CHECK = True

# TOR Failover Settings
TOR_AUTO_FAILOVER = True
TOR_FAILOVER_BLACKLIST_DURATION = 3600  # Blacklist problematic exit nodes for 1 hour
TOR_MAX_FAILURE_COUNT = 5  # Max failures before blacklisting exit node

# User Agent Rotation for TOR
TOR_ROTATE_USER_AGENTS = True
TOR_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/120.0",
]

# TOR Integration with Existing Middleware
DOWNLOADER_MIDDLEWARES = {
    "business_intel_scraper.backend.proxy.tor_middleware.TORProxyMiddleware": 585,
    "business_intel_scraper.backend.proxy.tor_middleware.TORStatsMiddleware": 590,
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,  # Disable default
    "scrapy.downloadermiddlewares.retry.RetryMiddleware": 550,
}

# Enhanced Request Settings for TOR
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 0.5
AUTOTHROTTLE_DEBUG = False

# TOR Circuit Path Configuration
TOR_CIRCUIT_PATH_LENGTH = 3  # Standard TOR path length
TOR_USE_GUARDS = True
TOR_ALLOW_SINGLE_HOP = False  # Security: Never use single hop

# TOR Bridge Configuration (for censored networks)
TOR_USE_BRIDGES = False
TOR_BRIDGE_TYPE = "obfs4"  # obfs4, meek, snowflake
TOR_BRIDGES = []  # List of bridge addresses

# TOR Hidden Service Support
TOR_ENABLE_HIDDEN_SERVICES = False
TOR_HIDDEN_SERVICE_TIMEOUT = 60

# TOR DNS Configuration
TOR_DNS_PORT = 8853
TOR_USE_TOR_DNS = True
TOR_DNS_FALLBACK = ["8.8.8.8", "1.1.1.1"]

# Logging Configuration for TOR
TOR_LOG_LEVEL = "INFO"
TOR_LOG_CIRCUIT_CHANGES = True
TOR_LOG_CONNECTION_TESTS = True
TOR_LOG_FAILURES = True
