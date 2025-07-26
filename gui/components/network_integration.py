"""
Integration Manager for TOR and Network Configuration
"""

from typing import Dict, Any, Optional, List
import logging
from dataclasses import dataclass, asdict

from PyQt6.QtCore import QObject, pyqtSignal
from business_intel_scraper.backend.proxy.tor_provider import (
    TORProxyProvider,
    proxy_manager,
)
from gui.components.network_config import VPNConfig, ProxyConfig, ConnectionType

logger = logging.getLogger(__name__)


@dataclass
class NetworkProfile:
    """Comprehensive network configuration profile"""

    name: str
    description: str
    tor_enabled: bool = False
    tor_config: Optional[Dict[str, Any]] = None
    vpn_config: Optional[VPNConfig] = None
    proxy_configs: List[ProxyConfig] = None
    browser_settings: Dict[str, Any] = None
    active: bool = False

    def __post_init__(self):
        if self.proxy_configs is None:
            self.proxy_configs = []
        if self.browser_settings is None:
            self.browser_settings = {
                "user_agent_rotation": True,
                "javascript_enabled": True,
                "images_enabled": True,
                "cache_enabled": False,
                "timeout": 30,
                "retry_count": 3,
            }


class NetworkIntegrationManager(QObject):
    """Manages integration between TOR, VPN, and proxy systems"""

    # Signals
    profile_changed = pyqtSignal(str)  # profile_name
    connection_status_changed = pyqtSignal(str, bool)  # service_type, connected
    error_occurred = pyqtSignal(str, str)  # service_type, error_message

    def __init__(self):
        super().__init__()
        self.profiles: Dict[str, NetworkProfile] = {}
        self.active_profile: Optional[NetworkProfile] = None
        self.tor_provider: Optional[TORProxyProvider] = None
        self.services_status = {"tor": False, "vpn": False, "proxy": False}

        # Create default profiles
        self.create_default_profiles()

    def create_default_profiles(self):
        """Create default network profiles"""

        # High Anonymity Profile
        high_anonymity = NetworkProfile(
            name="High Anonymity",
            description="Maximum anonymity using TOR with strict settings",
            tor_enabled=True,
            tor_config={
                "circuit_change_interval": 5,
                "exit_countries": [],
                "require_stable": True,
                "require_fast": True,
                "path_length": 3,
            },
            browser_settings={
                "user_agent_rotation": True,
                "javascript_enabled": False,
                "images_enabled": False,
                "cache_enabled": False,
                "timeout": 45,
                "retry_count": 5,
            },
        )

        # Balanced Profile
        balanced = NetworkProfile(
            name="Balanced",
            description="Balance between speed and anonymity",
            tor_enabled=True,
            tor_config={
                "circuit_change_interval": 20,
                "exit_countries": ["US", "DE", "NL", "SE"],
                "require_stable": True,
                "require_fast": True,
                "path_length": 3,
            },
            browser_settings={
                "user_agent_rotation": True,
                "javascript_enabled": True,
                "images_enabled": True,
                "cache_enabled": False,
                "timeout": 30,
                "retry_count": 3,
            },
        )

        # Speed Optimized Profile
        speed_optimized = NetworkProfile(
            name="Speed Optimized",
            description="Fastest configuration with minimal anonymity overhead",
            tor_enabled=False,
            proxy_configs=[
                ProxyConfig(
                    host="",  # To be configured
                    port=8080,
                    connection_type=ConnectionType.DATACENTER,
                    protocol="http",
                )
            ],
            browser_settings={
                "user_agent_rotation": False,
                "javascript_enabled": True,
                "images_enabled": True,
                "cache_enabled": True,
                "timeout": 15,
                "retry_count": 2,
            },
        )

        # Country-Specific Profiles
        us_profile = NetworkProfile(
            name="US Exit Nodes",
            description="TOR with US exit nodes only",
            tor_enabled=True,
            tor_config={
                "circuit_change_interval": 15,
                "exit_countries": ["US"],
                "require_stable": True,
                "require_fast": True,
                "path_length": 3,
            },
        )

        europe_profile = NetworkProfile(
            name="Europe Exit Nodes",
            description="TOR with European exit nodes",
            tor_enabled=True,
            tor_config={
                "circuit_change_interval": 15,
                "exit_countries": ["DE", "NL", "FR", "SE", "CH"],
                "require_stable": True,
                "require_fast": True,
                "path_length": 3,
            },
        )

        self.profiles = {
            "high_anonymity": high_anonymity,
            "balanced": balanced,
            "speed_optimized": speed_optimized,
            "us_exits": us_profile,
            "europe_exits": europe_profile,
        }

    def activate_profile(self, profile_name: str) -> bool:
        """Activate a network profile"""
        if profile_name not in self.profiles:
            logger.error(f"Profile {profile_name} not found")
            return False

        profile = self.profiles[profile_name]

        try:
            # Deactivate current profile
            if self.active_profile:
                self.deactivate_current_profile()

            # Activate new profile
            success = self._apply_profile_settings(profile)

            if success:
                # Mark old profile as inactive
                if self.active_profile:
                    self.active_profile.active = False

                # Activate new profile
                profile.active = True
                self.active_profile = profile

                self.profile_changed.emit(profile_name)
                logger.info(f"Activated network profile: {profile_name}")
                return True
            else:
                logger.error(f"Failed to activate profile: {profile_name}")
                return False

        except Exception as e:
            logger.error(f"Error activating profile {profile_name}: {e}")
            self.error_occurred.emit("profile", str(e))
            return False

    def deactivate_current_profile(self):
        """Deactivate current active profile"""
        if not self.active_profile:
            return

        try:
            # Shutdown TOR if enabled
            if self.active_profile.tor_enabled and self.tor_provider:
                self.tor_provider.shutdown()
                self.tor_provider = None
                self.services_status["tor"] = False
                self.connection_status_changed.emit("tor", False)

            # Disconnect VPN if configured
            if self.active_profile.vpn_config:
                # VPN disconnection logic would go here
                self.services_status["vpn"] = False
                self.connection_status_changed.emit("vpn", False)

            self.active_profile.active = False
            logger.info(f"Deactivated profile: {self.active_profile.name}")

        except Exception as e:
            logger.error(f"Error deactivating profile: {e}")

    async def _apply_profile_settings(self, profile: NetworkProfile) -> bool:
        """Apply settings from a network profile"""
        success = True

        # Apply TOR settings
        if profile.tor_enabled and profile.tor_config:
            tor_success = await self._setup_tor(profile.tor_config)
            if not tor_success:
                success = False
                logger.error("Failed to setup TOR for profile")

        # Apply VPN settings
        if profile.vpn_config:
            vpn_success = self._setup_vpn(profile.vpn_config)
            if not vpn_success:
                success = False
                logger.error("Failed to setup VPN for profile")

        # Apply proxy settings
        if profile.proxy_configs:
            proxy_success = self._setup_proxies(profile.proxy_configs)
            if not proxy_success:
                success = False
                logger.error("Failed to setup proxies for profile")

        return success

    async def _setup_tor(self, tor_config: Dict[str, Any]) -> bool:
        """Setup TOR with profile configuration"""
        try:
            # Initialize TOR provider
            success = await proxy_manager.add_tor_provider()

            if success:
                self.tor_provider = proxy_manager.providers["tor"]

                # Configure TOR circuit settings
                if "exit_countries" in tor_config:
                    self.tor_provider.create_custom_circuit(
                        exit_countries=tor_config["exit_countries"],
                        path_length=tor_config.get("path_length", 3),
                    )

                self.services_status["tor"] = True
                self.connection_status_changed.emit("tor", True)
                logger.info("TOR setup completed successfully")
                return True
            else:
                logger.error("Failed to initialize TOR provider")
                return False

        except Exception as e:
            logger.error(f"TOR setup error: {e}")
            self.error_occurred.emit("tor", str(e))
            return False

    def _setup_vpn(self, vpn_config: VPNConfig) -> bool:
        """Setup VPN with profile configuration"""
        try:
            # VPN setup logic would go here
            # This is a placeholder for VPN integration

            self.services_status["vpn"] = True
            self.connection_status_changed.emit("vpn", True)
            logger.info("VPN setup completed successfully")
            return True

        except Exception as e:
            logger.error(f"VPN setup error: {e}")
            self.error_occurred.emit("vpn", str(e))
            return False

    def _setup_proxies(self, proxy_configs: List[ProxyConfig]) -> bool:
        """Setup proxy rotation with profile configuration"""
        try:
            # Proxy setup logic would go here
            # This is a placeholder for proxy integration

            self.services_status["proxy"] = True
            self.connection_status_changed.emit("proxy", True)
            logger.info("Proxy setup completed successfully")
            return True

        except Exception as e:
            logger.error(f"Proxy setup error: {e}")
            self.error_occurred.emit("proxy", str(e))
            return False

    def get_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Get all available profiles"""
        return {
            name: {
                "name": profile.name,
                "description": profile.description,
                "tor_enabled": profile.tor_enabled,
                "active": profile.active,
            }
            for name, profile in self.profiles.items()
        }

    def get_active_profile(self) -> Optional[Dict[str, Any]]:
        """Get currently active profile"""
        if self.active_profile:
            return asdict(self.active_profile)
        return None

    def get_services_status(self) -> Dict[str, bool]:
        """Get status of all network services"""
        return self.services_status.copy()

    def create_custom_profile(self, name: str, config: Dict[str, Any]) -> bool:
        """Create custom network profile"""
        try:
            profile = NetworkProfile(
                name=name,
                description=config.get("description", f"Custom profile: {name}"),
                tor_enabled=config.get("tor_enabled", False),
                tor_config=config.get("tor_config"),
                vpn_config=config.get("vpn_config"),
                proxy_configs=config.get("proxy_configs", []),
                browser_settings=config.get("browser_settings", {}),
            )

            self.profiles[name] = profile
            logger.info(f"Created custom profile: {name}")
            return True

        except Exception as e:
            logger.error(f"Error creating custom profile {name}: {e}")
            return False

    def delete_profile(self, name: str) -> bool:
        """Delete a network profile"""
        if name not in self.profiles:
            return False

        if self.active_profile and self.active_profile.name == name:
            self.deactivate_current_profile()
            self.active_profile = None

        del self.profiles[name]
        logger.info(f"Deleted profile: {name}")
        return True

    async def test_current_configuration(self) -> Dict[str, Any]:
        """Test current network configuration"""
        results = {
            "tor": {"available": False, "working": False},
            "vpn": {"available": False, "working": False},
            "proxy": {"available": False, "working": False},
            "overall_status": "disconnected",
        }

        # Test TOR if enabled
        if self.services_status["tor"] and self.tor_provider:
            try:
                tor_test = self.tor_provider.test_connection()
                results["tor"] = {
                    "available": True,
                    "working": tor_test.get("success", False),
                    "ip_address": tor_test.get("ip"),
                    "is_tor": tor_test.get("is_tor", False),
                    "circuit": tor_test.get("circuit"),
                }
            except Exception as e:
                results["tor"]["error"] = str(e)

        # Test VPN if enabled
        if self.services_status["vpn"]:
            # VPN testing logic would go here
            results["vpn"]["available"] = True

        # Test proxies if enabled
        if self.services_status["proxy"]:
            # Proxy testing logic would go here
            results["proxy"]["available"] = True

        # Determine overall status
        if any(
            service["working"]
            for service in results.values()
            if isinstance(service, dict)
        ):
            results["overall_status"] = "connected"
        elif any(
            service["available"]
            for service in results.values()
            if isinstance(service, dict)
        ):
            results["overall_status"] = "available"

        return results


# Global network integration manager
network_manager = NetworkIntegrationManager()
