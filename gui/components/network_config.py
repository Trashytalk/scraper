"""
Network Configuration GUI with VPN Integration and Proxy Management
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QGroupBox, QLabel, QLineEdit, QPushButton, QComboBox,
                            QSpinBox, QCheckBox, QTableWidget, QTableWidgetItem,
                            QTabWidget, QTextEdit, QProgressBar, QSlider,
                            QListWidget, QSplitter, QHeaderView)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSettings
from PyQt6.QtGui import QColor, QPalette
import requests
import subprocess
import time
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ConnectionType(Enum):
    RESIDENTIAL = "residential"
    DATACENTER = "datacenter" 
    MOBILE = "mobile"

class VPNProvider(Enum):
    CYBERGHOST = "cyberghost"
    IPVANISH = "ipvanish"
    PROTON = "proton"
    MULLVAD = "mullvad"
    PIA = "private_internet_access"
    TUNNELBEAR = "tunnelbear"
    SURFSHARK = "surfshark"

@dataclass
class ProxyConfig:
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    protocol: str = "http"  # http, https, socks4, socks5
    connection_type: ConnectionType = ConnectionType.DATACENTER
    country: Optional[str] = None
    provider: Optional[str] = None
    score: float = 0.0
    last_tested: Optional[float] = None
    response_time: float = 0.0
    success_rate: float = 0.0

@dataclass 
class VPNConfig:
    provider: VPNProvider
    server: str
    username: str
    password: str
    protocol: str = "openvpn"
    auto_connect: bool = True
    kill_switch: bool = True
    dns_leak_protection: bool = True

class ProxyTester(QThread):
    """Test proxy performance and functionality"""
    
    test_completed = pyqtSignal(str, dict)  # proxy_id, results
    progress_updated = pyqtSignal(int)
    
    def __init__(self, proxies: List[ProxyConfig]):
        super().__init__()
        self.proxies = proxies
        self.test_urls = [
            "http://httpbin.org/ip",
            "https://api.ipify.org",
            "http://icanhazip.com"
        ]
        
    def run(self):
        """Test all proxies"""
        total = len(self.proxies)
        
        for i, proxy in enumerate(self.proxies):
            results = self.test_proxy(proxy)
            proxy_id = f"{proxy.host}:{proxy.port}"
            self.test_completed.emit(proxy_id, results)
            self.progress_updated.emit(int((i + 1) / total * 100))
            
    def test_proxy(self, proxy: ProxyConfig) -> Dict[str, Any]:
        """Test individual proxy"""
        results = {
            'working': False,
            'response_time': 0.0,
            'ip_address': None,
            'country': None,
            'error': None
        }
        
        proxy_url = f"{proxy.protocol}://"
        if proxy.username and proxy.password:
            proxy_url += f"{proxy.username}:{proxy.password}@"
        proxy_url += f"{proxy.host}:{proxy.port}"
        
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        
        start_time = time.time()
        
        try:
            response = requests.get(
                self.test_urls[0], 
                proxies=proxies, 
                timeout=10
            )
            
            if response.status_code == 200:
                results['working'] = True
                results['response_time'] = time.time() - start_time
                results['ip_address'] = response.json().get('origin')
                
        except Exception as e:
            results['error'] = str(e)
            
        return results

class VPNManager(QThread):
    """Manage VPN connections"""
    
    connection_changed = pyqtSignal(bool, str)  # connected, server
    status_updated = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.current_vpn = None
        self.connected = False
        
    def connect_vpn(self, vpn_config: VPNConfig):
        """Connect to VPN"""
        self.current_vpn = vpn_config
        self.start()
        
    def disconnect_vpn(self):
        """Disconnect from VPN"""
        if self.connected:
            self.disconnect_current()
            
    def run(self):
        """VPN connection thread"""
        if not self.current_vpn:
            return
            
        self.status_updated.emit("Connecting to VPN...")
        
        try:
            # Implementation depends on VPN provider
            success = self.connect_to_provider(self.current_vpn)
            
            if success:
                self.connected = True
                self.connection_changed.emit(True, self.current_vpn.server)
                self.status_updated.emit(f"Connected to {self.current_vpn.provider.value}")
            else:
                self.connection_changed.emit(False, "")
                self.status_updated.emit("VPN connection failed")
                
        except Exception as e:
            self.connection_changed.emit(False, "")
            self.status_updated.emit(f"VPN error: {str(e)}")
            
    def connect_to_provider(self, vpn_config: VPNConfig) -> bool:
        """Connect to specific VPN provider"""
        # This would implement provider-specific connection logic
        # For now, return a mock success
        time.sleep(2)  # Simulate connection time
        return True
        
    def disconnect_current(self):
        """Disconnect current VPN"""
        # Implementation for disconnecting
        self.connected = False
        self.connection_changed.emit(False, "")
        self.status_updated.emit("VPN disconnected")

class NetworkConfigWidget(QWidget):
    """Main network configuration widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.proxy_configs: List[ProxyConfig] = []
        self.vpn_configs: List[VPNConfig] = []
        self.proxy_tester = None
        self.vpn_manager = VPNManager()
        
        self.setup_ui()
        self.load_configurations()
        self.connect_signals()
        
    def setup_ui(self):
        """Setup the network configuration UI"""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Proxy configuration tab
        self.proxy_tab = self.create_proxy_tab()
        self.tab_widget.addTab(self.proxy_tab, "Proxy Management")
        
        # VPN configuration tab
        self.vpn_tab = self.create_vpn_tab()
        self.tab_widget.addTab(self.vpn_tab, "VPN Configuration")
        
        # Browser configuration tab
        self.browser_tab = self.create_browser_tab()
        self.tab_widget.addTab(self.browser_tab, "Browser Settings")
        
        layout.addWidget(self.tab_widget)
        
    def create_proxy_tab(self) -> QWidget:
        """Create proxy configuration tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Proxy controls
        controls_group = QGroupBox("Proxy Controls")
        controls_layout = QHBoxLayout(controls_group)
        
        self.add_proxy_btn = QPushButton("Add Proxy")
        self.import_proxies_btn = QPushButton("Import List")
        self.test_all_btn = QPushButton("Test All")
        self.auto_rotate_cb = QCheckBox("Auto Rotate")
        
        controls_layout.addWidget(self.add_proxy_btn)
        controls_layout.addWidget(self.import_proxies_btn)
        controls_layout.addWidget(self.test_all_btn)
        controls_layout.addWidget(self.auto_rotate_cb)
        controls_layout.addStretch()
        
        # Proxy table
        self.proxy_table = QTableWidget()
        self.proxy_table.setColumnCount(9)
        self.proxy_table.setHorizontalHeaderLabels([
            "Host", "Port", "Type", "Country", "Provider", 
            "Score", "Response Time", "Status", "Actions"
        ])
        self.proxy_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Test progress
        self.test_progress = QProgressBar()
        self.test_progress.setVisible(False)
        
        # Proxy filters
        filters_group = QGroupBox("Filters")
        filters_layout = QGridLayout(filters_group)
        
        filters_layout.addWidget(QLabel("Type:"), 0, 0)
        self.type_filter = QComboBox()
        self.type_filter.addItems(["All", "Residential", "Datacenter", "Mobile"])
        filters_layout.addWidget(self.type_filter, 0, 1)
        
        filters_layout.addWidget(QLabel("Country:"), 0, 2)
        self.country_filter = QComboBox()
        self.country_filter.addItems(["All", "US", "UK", "DE", "CA", "AU"])
        filters_layout.addWidget(self.country_filter, 0, 3)
        
        filters_layout.addWidget(QLabel("Min Score:"), 1, 0)
        self.score_filter = QSlider(Qt.Orientation.Horizontal)
        self.score_filter.setRange(0, 100)
        self.score_filter.setValue(0)
        filters_layout.addWidget(self.score_filter, 1, 1, 1, 3)
        
        layout.addWidget(controls_group)
        layout.addWidget(filters_group)
        layout.addWidget(self.proxy_table)
        layout.addWidget(self.test_progress)
        
        return widget
        
    def create_vpn_tab(self) -> QWidget:
        """Create VPN configuration tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # VPN provider selection
        provider_group = QGroupBox("VPN Provider")
        provider_layout = QGridLayout(provider_group)
        
        provider_layout.addWidget(QLabel("Provider:"), 0, 0)
        self.vpn_provider_combo = QComboBox()
        self.vpn_provider_combo.addItems([provider.value for provider in VPNProvider])
        provider_layout.addWidget(self.vpn_provider_combo, 0, 1)
        
        provider_layout.addWidget(QLabel("Username:"), 1, 0)
        self.vpn_username = QLineEdit()
        provider_layout.addWidget(self.vpn_username, 1, 1)
        
        provider_layout.addWidget(QLabel("Password:"), 2, 0)
        self.vpn_password = QLineEdit()
        self.vpn_password.setEchoMode(QLineEdit.EchoMode.Password)
        provider_layout.addWidget(self.vpn_password, 2, 1)
        
        # Server selection
        server_group = QGroupBox("Server Selection")
        server_layout = QVBoxLayout(server_group)
        
        server_controls = QHBoxLayout()
        server_controls.addWidget(QLabel("Server:"))
        self.vpn_server_combo = QComboBox()
        server_controls.addWidget(self.vpn_server_combo)
        self.refresh_servers_btn = QPushButton("Refresh")
        server_controls.addWidget(self.refresh_servers_btn)
        
        server_layout.addLayout(server_controls)
        
        # VPN options
        options_group = QGroupBox("Connection Options")
        options_layout = QGridLayout(options_group)
        
        self.auto_connect_cb = QCheckBox("Auto Connect on Startup")
        options_layout.addWidget(self.auto_connect_cb, 0, 0)
        
        self.kill_switch_cb = QCheckBox("Kill Switch")
        self.kill_switch_cb.setChecked(True)
        options_layout.addWidget(self.kill_switch_cb, 0, 1)
        
        self.dns_protection_cb = QCheckBox("DNS Leak Protection")
        self.dns_protection_cb.setChecked(True)
        options_layout.addWidget(self.dns_protection_cb, 1, 0)
        
        self.auto_reconnect_cb = QCheckBox("Auto Reconnect")
        self.auto_reconnect_cb.setChecked(True)
        options_layout.addWidget(self.auto_reconnect_cb, 1, 1)
        
        # Connection controls
        connection_group = QGroupBox("Connection")
        connection_layout = QHBoxLayout(connection_group)
        
        self.connect_vpn_btn = QPushButton("Connect")
        self.disconnect_vpn_btn = QPushButton("Disconnect")
        self.disconnect_vpn_btn.setEnabled(False)
        
        connection_layout.addWidget(self.connect_vpn_btn)
        connection_layout.addWidget(self.disconnect_vpn_btn)
        connection_layout.addStretch()
        
        # Status
        self.vpn_status_label = QLabel("Status: Disconnected")
        self.vpn_status_label.setStyleSheet("color: red;")
        
        layout.addWidget(provider_group)
        layout.addWidget(server_group)
        layout.addWidget(options_group)
        layout.addWidget(connection_group)
        layout.addWidget(self.vpn_status_label)
        layout.addStretch()
        
        return widget
        
    def create_browser_tab(self) -> QWidget:
        """Create browser configuration tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Browser mode
        mode_group = QGroupBox("Browser Mode")
        mode_layout = QGridLayout(mode_group)
        
        mode_layout.addWidget(QLabel("Mode:"), 0, 0)
        self.browser_mode_combo = QComboBox()
        self.browser_mode_combo.addItems(["Headless", "Headed", "Auto"])
        mode_layout.addWidget(self.browser_mode_combo, 0, 1)
        
        mode_layout.addWidget(QLabel("User Agent:"), 1, 0)
        self.user_agent_combo = QComboBox()
        self.user_agent_combo.setEditable(True)
        self.user_agent_combo.addItems([
            "Chrome/Windows",
            "Firefox/Windows", 
            "Safari/macOS",
            "Chrome/Linux",
            "Mobile/Android",
            "Custom..."
        ])
        mode_layout.addWidget(self.user_agent_combo, 1, 1)
        
        # Request settings
        request_group = QGroupBox("Request Settings")
        request_layout = QGridLayout(request_group)
        
        request_layout.addWidget(QLabel("Timeout (s):"), 0, 0)
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 300)
        self.timeout_spin.setValue(30)
        request_layout.addWidget(self.timeout_spin, 0, 1)
        
        request_layout.addWidget(QLabel("Delay (s):"), 1, 0)
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(0, 60)
        self.delay_spin.setValue(1)
        request_layout.addWidget(self.delay_spin, 1, 1)
        
        request_layout.addWidget(QLabel("Retry Count:"), 2, 0)
        self.retry_spin = QSpinBox()
        self.retry_spin.setRange(0, 10)
        self.retry_spin.setValue(3)
        request_layout.addWidget(self.retry_spin, 2, 1)
        
        # Advanced options
        advanced_group = QGroupBox("Advanced Options")
        advanced_layout = QGridLayout(advanced_group)
        
        self.javascript_cb = QCheckBox("Enable JavaScript")
        self.javascript_cb.setChecked(True)
        advanced_layout.addWidget(self.javascript_cb, 0, 0)
        
        self.images_cb = QCheckBox("Load Images")
        self.images_cb.setChecked(True)
        advanced_layout.addWidget(self.images_cb, 0, 1)
        
        self.css_cb = QCheckBox("Load CSS")
        self.css_cb.setChecked(True)
        advanced_layout.addWidget(self.css_cb, 1, 0)
        
        self.cache_cb = QCheckBox("Enable Cache")
        self.cache_cb.setChecked(False)
        advanced_layout.addWidget(self.cache_cb, 1, 1)
        
        layout.addWidget(mode_group)
        layout.addWidget(request_group)
        layout.addWidget(advanced_group)
        layout.addStretch()
        
        return widget
        
    def connect_signals(self):
        """Connect UI signals"""
        # Proxy signals
        self.add_proxy_btn.clicked.connect(self.add_proxy)
        self.import_proxies_btn.clicked.connect(self.import_proxies)
        self.test_all_btn.clicked.connect(self.test_all_proxies)
        
        # VPN signals
        self.connect_vpn_btn.clicked.connect(self.connect_vpn)
        self.disconnect_vpn_btn.clicked.connect(self.disconnect_vpn)
        self.refresh_servers_btn.clicked.connect(self.refresh_servers)
        
        # VPN manager signals
        self.vpn_manager.connection_changed.connect(self.on_vpn_connection_changed)
        self.vpn_manager.status_updated.connect(self.on_vpn_status_updated)
        
    def add_proxy(self):
        """Add new proxy configuration"""
        # Implementation for adding proxy dialog
        pass
        
    def import_proxies(self):
        """Import proxy list from file"""
        # Implementation for importing proxies
        pass
        
    def test_all_proxies(self):
        """Test all configured proxies"""
        if not self.proxy_configs:
            return
            
        self.test_progress.setVisible(True)
        self.test_progress.setValue(0)
        
        self.proxy_tester = ProxyTester(self.proxy_configs)
        self.proxy_tester.test_completed.connect(self.on_proxy_test_completed)
        self.proxy_tester.progress_updated.connect(self.test_progress.setValue)
        self.proxy_tester.finished.connect(lambda: self.test_progress.setVisible(False))
        self.proxy_tester.start()
        
    def on_proxy_test_completed(self, proxy_id: str, results: Dict[str, Any]):
        """Handle proxy test completion"""
        # Update proxy table with test results
        logger.info(f"Proxy {proxy_id} test completed: {results}")
        
    def connect_vpn(self):
        """Connect to selected VPN"""
        provider = VPNProvider(self.vpn_provider_combo.currentText())
        username = self.vpn_username.text()
        password = self.vpn_password.text()
        server = self.vpn_server_combo.currentText()
        
        if not all([username, password, server]):
            return
            
        vpn_config = VPNConfig(
            provider=provider,
            server=server,
            username=username,
            password=password,
            auto_connect=self.auto_connect_cb.isChecked(),
            kill_switch=self.kill_switch_cb.isChecked(),
            dns_leak_protection=self.dns_protection_cb.isChecked()
        )
        
        self.vpn_manager.connect_vpn(vpn_config)
        
    def disconnect_vpn(self):
        """Disconnect from VPN"""
        self.vpn_manager.disconnect_vpn()
        
    def refresh_servers(self):
        """Refresh available VPN servers"""
        # Implementation for refreshing server list
        pass
        
    def on_vpn_connection_changed(self, connected: bool, server: str):
        """Handle VPN connection state change"""
        self.connect_vpn_btn.setEnabled(not connected)
        self.disconnect_vpn_btn.setEnabled(connected)
        
        if connected:
            self.vpn_status_label.setText(f"Status: Connected to {server}")
            self.vpn_status_label.setStyleSheet("color: green;")
        else:
            self.vpn_status_label.setText("Status: Disconnected")
            self.vpn_status_label.setStyleSheet("color: red;")
            
    def on_vpn_status_updated(self, status: str):
        """Handle VPN status updates"""
        self.vpn_status_label.setText(f"Status: {status}")
        
    def load_configurations(self):
        """Load saved configurations"""
        settings = QSettings()
        # Load proxy and VPN configurations from settings
        pass
        
    def save_configurations(self):
        """Save current configurations"""
        settings = QSettings()
        # Save proxy and VPN configurations to settings
        pass
