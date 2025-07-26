"""
API Configuration Template for Data Enrichment Services

Copy this file to 'api_config.py' and fill in your actual API credentials.
Never commit api_config.py with real credentials to version control.
"""

# Data Enrichment API Credentials
API_CREDENTIALS = {
    # Clearbit API for person and company enrichment
    # Sign up at: https://clearbit.com/
    "clearbit": {
        "api_key": "your_clearbit_api_key_here",
        "enabled": False,
        "rate_limit": 1.0,  # seconds between requests
        "monthly_quota": 1000,
    },
    # FullContact API for contact information enrichment
    # Sign up at: https://www.fullcontact.com/
    "fullcontact": {
        "api_key": "your_fullcontact_api_key_here",
        "enabled": False,
        "rate_limit": 1.0,
        "monthly_quota": 1000,
    },
    # Hunter.io for email verification and finding
    # Sign up at: https://hunter.io/
    "hunter": {
        "api_key": "your_hunter_api_key_here",
        "enabled": False,
        "rate_limit": 1.0,
        "monthly_quota": 1000,
    },
    # Shodan for IP and domain intelligence
    # Sign up at: https://www.shodan.io/
    "shodan": {
        "api_key": "your_shodan_api_key_here",
        "enabled": False,
        "rate_limit": 1.0,
        "monthly_quota": 100,
    },
    # VirusTotal for security analysis
    # Sign up at: https://www.virustotal.com/
    "virustotal": {
        "api_key": "your_virustotal_api_key_here",
        "enabled": False,
        "rate_limit": 4.0,  # Free tier: 15 requests per minute
        "monthly_quota": 500,
    },
    # Have I Been Pwned for breach checking (v3 API requires key)
    # Get key at: https://haveibeenpwned.com/API/Key
    "haveibeenpwned": {
        "api_key": "your_hibp_api_key_here",
        "enabled": False,
        "rate_limit": 1.5,  # Rate limited to avoid blocking
        "monthly_quota": 1000,
    },
}

# VPN Provider Credentials
VPN_PROVIDERS = {
    "cyberghost": {
        "username": "your_cyberghost_username",
        "password": "your_cyberghost_password",
        "enabled": False,
        "server_regions": ["US", "UK", "DE", "FR", "CA"],
    },
    "ipvanish": {
        "username": "your_ipvanish_username",
        "password": "your_ipvanish_password",
        "enabled": False,
        "server_regions": ["US", "UK", "DE", "FR", "CA"],
    },
    "protonvpn": {
        "username": "your_proton_username",
        "password": "your_proton_password",
        "enabled": False,
        "server_regions": ["US", "UK", "DE", "FR", "CA"],
    },
    "mullvad": {
        "account_number": "your_mullvad_account_number",
        "enabled": False,
        "server_regions": ["US", "UK", "DE", "FR", "CA"],
    },
    "pia": {
        "username": "your_pia_username",
        "password": "your_pia_password",
        "enabled": False,
        "server_regions": ["US", "UK", "DE", "FR", "CA"],
    },
}

# Proxy Pool Configuration
PROXY_POOLS = {
    "residential": {
        "provider": "your_residential_proxy_provider",
        "username": "your_proxy_username",
        "password": "your_proxy_password",
        "endpoints": ["proxy1.provider.com:8080", "proxy2.provider.com:8080"],
        "enabled": False,
    },
    "datacenter": {
        "provider": "your_datacenter_proxy_provider",
        "username": "your_proxy_username",
        "password": "your_proxy_password",
        "endpoints": ["dc1.provider.com:3128", "dc2.provider.com:3128"],
        "enabled": False,
    },
    "mobile": {
        "provider": "your_mobile_proxy_provider",
        "username": "your_proxy_username",
        "password": "your_proxy_password",
        "endpoints": ["mobile1.provider.com:8000", "mobile2.provider.com:8000"],
        "enabled": False,
    },
}

# TOR Configuration
TOR_CONFIG = {
    "enabled": True,  # TOR can work without external credentials
    "control_port": 9051,
    "socks_port": 9050,
    "control_password": "",  # Leave empty for default setup
    "bridge_config": {
        "use_bridges": False,
        "bridge_type": "obfs4",  # obfs4, webtunnel, snowflake
        "custom_bridges": [],
    },
    "exit_nodes": {
        "country_codes": ["US", "DE", "NL"],  # Preferred exit countries
        "exclude_countries": ["CN", "RU", "IR"],  # Countries to avoid
    },
}

# SpiderFoot Integration
SPIDERFOOT_CONFIG = {
    "base_url": "http://localhost:5001",  # Default SpiderFoot API URL
    "enabled": False,  # Set to True if you have SpiderFoot running
    "modules": {
        # Enable/disable specific SpiderFoot modules
        "sfp_dnsresolve": True,
        "sfp_whois": True,
        "sfp_shodan": False,  # Requires Shodan API key above
        "sfp_virustotal": False,  # Requires VirusTotal API key above
        "sfp_haveibeenpwned": False,  # Requires HIBP API key above
        "sfp_hunter": False,  # Requires Hunter API key above
    },
}

# Security Settings
SECURITY_CONFIG = {
    "encrypt_credentials": True,
    "credential_storage": "local",  # local, keyring, env
    "rate_limit_enabled": True,
    "request_timeout": 30,
    "max_retries": 3,
    "user_agents_rotation": True,
    "respect_robots_txt": True,
}

# Performance Settings
PERFORMANCE_CONFIG = {
    "max_concurrent_requests": 10,
    "request_delay": 1.0,
    "connection_pool_size": 20,
    "enable_caching": True,
    "cache_ttl": 3600,  # 1 hour
    "use_compression": True,
}
