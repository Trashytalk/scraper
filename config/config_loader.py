"""
Configuration loader for API credentials and settings
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Safely load API configuration from various sources"""

    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir) if config_dir else Path(__file__).parent
        self.config_file = self.config_dir / "api_config.py"
        self.template_file = self.config_dir / "api_config_template.py"

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or environment variables"""
        config = {}

        # Try to load from api_config.py first
        if self.config_file.exists():
            try:
                config = self._load_from_file()
                logger.info("Loaded configuration from api_config.py")
            except Exception as e:
                logger.error(f"Error loading config file: {e}")

        # Fallback to environment variables
        if not config:
            config = self._load_from_env()
            logger.info("Loaded configuration from environment variables")

        # If no config found, create template
        if not config:
            self._create_template()
            config = self._get_default_config()
            logger.warning(
                "No configuration found. Created template file. Using defaults."
            )

        return config

    def _load_from_file(self) -> Dict[str, Any]:
        """Load configuration from Python file"""
        import importlib.util

        spec = importlib.util.spec_from_file_location("api_config", self.config_file)
        if spec is None or spec.loader is None:
            raise ImportError("Could not load api_config module")

        api_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(api_config)

        return {
            "api_credentials": getattr(api_config, "API_CREDENTIALS", {}),
            "vpn_providers": getattr(api_config, "VPN_PROVIDERS", {}),
            "proxy_pools": getattr(api_config, "PROXY_POOLS", {}),
            "tor_config": getattr(api_config, "TOR_CONFIG", {}),
            "spiderfoot_config": getattr(api_config, "SPIDERFOOT_CONFIG", {}),
            "security_config": getattr(api_config, "SECURITY_CONFIG", {}),
            "performance_config": getattr(api_config, "PERFORMANCE_CONFIG", {}),
        }

    def _load_from_env(self) -> Dict[str, Any]:
        """Load configuration from environment variables"""
        config = {
            "api_credentials": {},
            "vpn_providers": {},
            "proxy_pools": {},
            "tor_config": {},
            "spiderfoot_config": {},
            "security_config": {},
            "performance_config": {},
        }

        # API credentials from environment
        api_keys = {
            "clearbit": os.getenv("CLEARBIT_API_KEY"),
            "fullcontact": os.getenv("FULLCONTACT_API_KEY"),
            "hunter": os.getenv("HUNTER_API_KEY"),
            "shodan": os.getenv("SHODAN_API_KEY"),
            "virustotal": os.getenv("VIRUSTOTAL_API_KEY"),
            "haveibeenpwned": os.getenv("HIBP_API_KEY"),
        }

        for service, api_key in api_keys.items():
            if api_key:
                config["api_credentials"][service] = {
                    "api_key": api_key,
                    "enabled": True,
                    "rate_limit": 1.0,
                    "monthly_quota": 1000,
                }

        # VPN credentials from environment
        vpn_services = ["cyberghost", "ipvanish", "protonvpn", "mullvad", "pia"]
        for service in vpn_services:
            username = os.getenv(f"{service.upper()}_USERNAME")
            password = os.getenv(f"{service.upper()}_PASSWORD")
            if username and password:
                config["vpn_providers"][service] = {
                    "username": username,
                    "password": password,
                    "enabled": True,
                    "server_regions": ["US", "UK", "DE", "FR", "CA"],
                }

        # TOR configuration
        config["tor_config"] = {
            "enabled": True,
            "control_port": int(os.getenv("TOR_CONTROL_PORT", "9051")),
            "socks_port": int(os.getenv("TOR_SOCKS_PORT", "9050")),
            "control_password": os.getenv("TOR_CONTROL_PASSWORD", ""),
            "exit_nodes": {
                "country_codes": os.getenv("TOR_EXIT_COUNTRIES", "US,DE,NL").split(","),
                "exclude_countries": os.getenv(
                    "TOR_EXCLUDE_COUNTRIES", "CN,RU,IR"
                ).split(","),
            },
        }

        # SpiderFoot configuration
        config["spiderfoot_config"] = {
            "base_url": os.getenv("SPIDERFOOT_URL", "http://localhost:5001"),
            "enabled": os.getenv("SPIDERFOOT_ENABLED", "false").lower() == "true",
        }

        return config if any(config["api_credentials"].values()) else {}

    def _create_template(self):
        """Create template configuration file"""
        if not self.config_file.exists() and self.template_file.exists():
            try:
                import shutil

                shutil.copy2(self.template_file, self.config_file)
                logger.info(f"Created configuration template at {self.config_file}")
            except Exception as e:
                logger.error(f"Could not create config template: {e}")

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration with TOR enabled"""
        return {
            "api_credentials": {},
            "vpn_providers": {},
            "proxy_pools": {},
            "tor_config": {
                "enabled": True,
                "control_port": 9051,
                "socks_port": 9050,
                "control_password": "",
                "bridge_config": {
                    "use_bridges": False,
                    "bridge_type": "obfs4",
                    "custom_bridges": [],
                },
                "exit_nodes": {
                    "country_codes": ["US", "DE", "NL"],
                    "exclude_countries": ["CN", "RU", "IR"],
                },
            },
            "spiderfoot_config": {
                "base_url": "http://localhost:5001",
                "enabled": False,
            },
            "security_config": {
                "encrypt_credentials": True,
                "credential_storage": "local",
                "rate_limit_enabled": True,
                "request_timeout": 30,
                "max_retries": 3,
            },
            "performance_config": {
                "max_concurrent_requests": 10,
                "request_delay": 1.0,
                "connection_pool_size": 20,
                "enable_caching": True,
                "cache_ttl": 3600,
            },
        }

    def save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        try:
            with open(self.config_file, "w") as f:
                f.write("# Auto-generated API configuration\n")
                f.write("# Edit this file to configure your API credentials\n\n")

                for key, value in config.items():
                    f.write(f"{key.upper()} = {repr(value)}\n\n")

            logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")


# Global configuration loader instance
config_loader = ConfigLoader()


def get_config() -> Dict[str, Any]:
    """Get application configuration"""
    return config_loader.load_config()


def save_config(config: Dict[str, Any]):
    """Save application configuration"""
    config_loader.save_config(config)
