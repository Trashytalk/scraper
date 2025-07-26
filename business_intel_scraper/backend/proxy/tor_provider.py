"""
TOR Proxy Provider Integration with Existing Proxy Management System
"""

import logging
from typing import Optional, Dict, Any, List

from business_intel_scraper.backend.proxy.provider import ProxyProvider
from gui.components.tor_integration import (
    TORController,
    CircuitConfig,
    TORFailureHandler,
)

logger = logging.getLogger(__name__)


class TORProxyProvider(ProxyProvider):
    """TOR proxy provider that integrates with the existing proxy management system"""

    def __init__(
        self,
        control_port: int = 9051,
        socks_port: int = 9050,
        password: Optional[str] = None,
    ):
        super().__init__()
        self.control_port = control_port
        self.socks_port = socks_port
        self.password = password
        self.tor_controller = TORController()
        self.failure_handler = TORFailureHandler(self.tor_controller)
        self.current_circuit = None
        self.circuit_config = CircuitConfig()

    async def initialize(self) -> bool:
        """Initialize TOR connection"""
        try:
            success = self.tor_controller.connect(self.control_port, self.password)
            if success:
                # Create initial circuit
                self.current_circuit = self.tor_controller.create_circuit(
                    self.circuit_config
                )
                logger.info("TOR proxy provider initialized successfully")
                return True
            else:
                logger.error("Failed to connect to TOR control port")
                return False
        except Exception as e:
            logger.error(f"Failed to initialize TOR proxy provider: {e}")
            return False

    def get_proxy(self) -> str:
        """Get current TOR proxy configuration"""
        return f"socks5://127.0.0.1:{self.socks_port}"

    def get_proxies_dict(self) -> Dict[str, str]:
        """Get proxy configuration dictionary for requests"""
        proxy_url = f"socks5://127.0.0.1:{self.socks_port}"
        return {"http": proxy_url, "https": proxy_url}

    def is_available(self) -> bool:
        """Check if TOR proxy is available"""
        return self.tor_controller.is_connected

    def new_identity(self) -> bool:
        """Request new TOR identity"""
        try:
            success = self.tor_controller.new_identity()
            if success:
                # Create new circuit after identity change
                old_circuit = self.current_circuit
                self.current_circuit = self.tor_controller.create_circuit(
                    self.circuit_config
                )

                # Close old circuit
                if old_circuit:
                    self.tor_controller.close_circuit(old_circuit)

                logger.info("TOR identity changed successfully")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to change TOR identity: {e}")
            return False

    def create_custom_circuit(
        self, exit_countries: Optional[List[str]] = None, path_length: int = 3
    ) -> Optional[str]:
        """Create custom TOR circuit"""
        try:
            config = CircuitConfig(
                path_length=path_length, require_countries=exit_countries
            )

            circuit_id = self.tor_controller.create_circuit(config)

            if circuit_id:
                # Close current circuit
                if self.current_circuit:
                    self.tor_controller.close_circuit(self.current_circuit)
                self.current_circuit = circuit_id
                logger.info(f"Created custom TOR circuit: {circuit_id}")
                return circuit_id
            else:
                logger.error("Failed to create custom TOR circuit")
                return None

        except Exception as e:
            logger.error(f"Error creating custom TOR circuit: {e}")
            return None

    def handle_failure(self) -> bool:
        """Handle proxy failure by creating new circuit"""
        try:
            if self.current_circuit:
                # Use failure handler to create recovery circuit
                new_circuit = self.failure_handler.handle_circuit_failure(
                    self.current_circuit, self.circuit_config
                )

                if new_circuit:
                    self.current_circuit = new_circuit
                    logger.info(f"Recovered from TOR circuit failure: {new_circuit}")
                    return True
                else:
                    # Fallback to new identity
                    return self.new_identity()
            else:
                # Create new circuit
                self.current_circuit = self.tor_controller.create_circuit(
                    self.circuit_config
                )
                return self.current_circuit is not None

        except Exception as e:
            logger.error(f"Failed to handle TOR proxy failure: {e}")
            return False

    def get_circuit_info(self) -> Dict[str, Any]:
        """Get information about current TOR circuit"""
        try:
            circuits = self.tor_controller.get_circuits()

            for circuit in circuits:
                if circuit["id"] == self.current_circuit:
                    return {
                        "circuit_id": circuit["id"],
                        "status": circuit["status"],
                        "path": circuit["path"],
                        "created": circuit.get("created"),
                        "purpose": circuit.get("purpose"),
                    }

            return {"error": "Current circuit not found"}

        except Exception as e:
            logger.error(f"Failed to get circuit info: {e}")
            return {"error": str(e)}

    def test_connection(self) -> Dict[str, Any]:
        """Test TOR connection"""
        try:
            result = self.tor_controller.test_connection()

            # Add circuit information to test result
            if result.get("success"):
                circuit_info = self.get_circuit_info()
                result["circuit"] = circuit_info

            return result

        except Exception as e:
            logger.error(f"TOR connection test failed: {e}")
            return {"success": False, "error": str(e)}

    def shutdown(self):
        """Shutdown TOR proxy provider"""
        try:
            if self.current_circuit:
                self.tor_controller.close_circuit(self.current_circuit)
            self.tor_controller.disconnect()
            logger.info("TOR proxy provider shut down successfully")
        except Exception as e:
            logger.error(f"Error shutting down TOR proxy provider: {e}")


class EnhancedProxyManager:
    """Enhanced proxy manager with TOR integration"""

    def __init__(self):
        self.providers = {}
        self.tor_provider = None
        self.active_provider = None

    async def add_tor_provider(
        self,
        control_port: int = 9051,
        socks_port: int = 9050,
        password: Optional[str] = None,
    ) -> bool:
        """Add TOR proxy provider"""
        try:
            self.tor_provider = TORProxyProvider(control_port, socks_port, password)
            success = await self.tor_provider.initialize()

            if success:
                self.providers["tor"] = self.tor_provider
                logger.info("TOR provider added to proxy manager")
                return True
            else:
                logger.error("Failed to add TOR provider")
                return False

        except Exception as e:
            logger.error(f"Error adding TOR provider: {e}")
            return False

    def set_active_provider(self, provider_name: str) -> bool:
        """Set active proxy provider"""
        if provider_name in self.providers:
            provider = self.providers[provider_name]
            if provider.is_available():
                self.active_provider = provider
                logger.info(f"Active proxy provider set to: {provider_name}")
                return True
            else:
                logger.error(f"Provider {provider_name} is not available")
                return False
        else:
            logger.error(f"Provider {provider_name} not found")
            return False

    def get_current_proxy(self) -> Optional[str]:
        """Get current active proxy"""
        if self.active_provider:
            return self.active_provider.get_proxy()
        return None

    def get_proxies_dict(self) -> Optional[Dict[str, str]]:
        """Get proxy configuration for requests"""
        if self.active_provider and hasattr(self.active_provider, "get_proxies_dict"):
            return self.active_provider.get_proxies_dict()
        elif self.active_provider:
            proxy = self.active_provider.get_proxy()
            return {"http": proxy, "https": proxy}
        return None

    def handle_proxy_failure(self) -> bool:
        """Handle active proxy failure"""
        if self.active_provider and hasattr(self.active_provider, "handle_failure"):
            return self.active_provider.handle_failure()
        return False

    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all providers"""
        status = {}

        for name, provider in self.providers.items():
            provider_status = {
                "available": provider.is_available(),
                "type": type(provider).__name__,
            }

            # Add TOR-specific information
            if isinstance(provider, TORProxyProvider):
                try:
                    circuit_info = provider.get_circuit_info()
                    connection_test = provider.test_connection()

                    provider_status.update(
                        {
                            "circuit": circuit_info,
                            "connection_test": connection_test,
                            "control_port": provider.control_port,
                            "socks_port": provider.socks_port,
                        }
                    )
                except Exception as e:
                    provider_status["error"] = str(e)

            status[name] = provider_status

        return status


# Global enhanced proxy manager instance
proxy_manager = EnhancedProxyManager()
