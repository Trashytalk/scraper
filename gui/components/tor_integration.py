"""
TOR Integration with Preconfigured Exit Nodes and Circuit Management
"""
from PyQt6.QtCore import QThread, pyqtSignal, QTimer
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                            QLabel, QPushButton, QComboBox, QSpinBox,
                            QCheckBox, QListWidget, QTextEdit, QProgressBar,
                            QTableWidget, QTableWidgetItem, QGridLayout)
import stem
from stem import Signal
from stem.control import Controller
from stem.descriptor.remote import DescriptorDownloader
import requests
import socks
import socket
import subprocess
import json
import time
import random
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    BUILDING = "BUILDING"
    BUILT = "BUILT"
    FAILED = "FAILED"
    CLOSED = "CLOSED"

@dataclass
class ExitNode:
    """TOR exit node configuration"""
    fingerprint: str
    nickname: str
    country_code: str
    ip_address: str
    bandwidth: int
    flags: List[str]
    contact: Optional[str] = None
    is_stable: bool = False
    is_fast: bool = False
    is_guard: bool = False
    uptime: Optional[int] = None

@dataclass
class CircuitConfig:
    """TOR circuit configuration"""
    circuit_id: Optional[str] = None
    path_length: int = 3
    entry_guards: Optional[List[str]] = None
    middle_relays: Optional[List[str]] = None
    exit_nodes: Optional[List[str]] = None
    exclude_countries: Optional[List[str]] = None
    require_countries: Optional[List[str]] = None
    max_circuit_age: int = 600  # seconds
    
class TORController:
    """TOR network controller"""
    
    def __init__(self):
        self.controller = None
        self.is_connected = False
        self.circuits = {}
        self.exit_nodes = []
        self.control_port = 9051
        self.socks_port = 9050
        self.tor_process = None
        
    def connect(self, control_port: int = 9051, password: Optional[str] = None) -> bool:
        """Connect to TOR control port"""
        try:
            self.control_port = control_port
            self.controller = Controller.from_port(port=control_port)
            
            if password:
                self.controller.authenticate(password=password)
            else:
                self.controller.authenticate()
                
            self.is_connected = True
            logger.info("Connected to TOR control port")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to TOR: {e}")
            return False
            
    def disconnect(self):
        """Disconnect from TOR"""
        if self.controller:
            self.controller.close()
            self.is_connected = False
            
    def get_circuits(self) -> List[Dict[str, Any]]:
        """Get current TOR circuits"""
        if not self.is_connected:
            return []
            
        circuits = []
        try:
            for circuit in self.controller.get_circuits():
                circuit_info = {
                    'id': circuit.id,
                    'status': circuit.status.name,
                    'path': [f"{relay.fingerprint} ({relay.nickname})" for relay in circuit.path],
                    'build_flags': circuit.build_flags,
                    'purpose': circuit.purpose,
                    'created': circuit.created
                }
                circuits.append(circuit_info)
        except Exception as e:
            logger.error(f"Failed to get circuits: {e}")
            
        return circuits
        
    def create_circuit(self, config: CircuitConfig) -> Optional[str]:
        """Create new TOR circuit with specified configuration"""
        if not self.is_connected:
            return None
            
        try:
            path = []
            
            # Build circuit path
            if config.entry_guards:
                path.extend(config.entry_guards[:1])
                
            if config.middle_relays:
                path.extend(config.middle_relays[:config.path_length-2])
            else:
                # Let TOR choose middle relays
                path.extend([None] * (config.path_length - len(path) - 1))
                
            if config.exit_nodes:
                path.append(random.choice(config.exit_nodes))
                
            # Create circuit
            circuit_id = self.controller.new_circuit(path=path if any(path) else None)
            
            # Wait for circuit to build
            start_time = time.time()
            while time.time() - start_time < 30:  # 30 second timeout
                circuit = self.controller.get_circuit(circuit_id)
                if circuit.status == stem.CircStatus.BUILT:
                    logger.info(f"Circuit {circuit_id} built successfully")
                    return circuit_id
                elif circuit.status == stem.CircStatus.FAILED:
                    logger.error(f"Circuit {circuit_id} failed to build")
                    return None
                time.sleep(1)
                
            logger.warning(f"Circuit {circuit_id} build timeout")
            return None
            
        except Exception as e:
            logger.error(f"Failed to create circuit: {e}")
            return None
            
    def close_circuit(self, circuit_id: str) -> bool:
        """Close TOR circuit"""
        if not self.is_connected:
            return False
            
        try:
            self.controller.close_circuit(circuit_id)
            logger.info(f"Circuit {circuit_id} closed")
            return True
        except Exception as e:
            logger.error(f"Failed to close circuit {circuit_id}: {e}")
            return False
            
    def get_exit_nodes(self, countries: Optional[List[str]] = None) -> List[ExitNode]:
        """Get available exit nodes"""
        if not self.is_connected:
            return []
            
        exit_nodes = []
        try:
            for desc in self.controller.get_network_statuses():
                if 'Exit' in desc.flags and 'Running' in desc.flags:
                    if countries and desc.country_code not in countries:
                        continue
                        
                    node = ExitNode(
                        fingerprint=desc.fingerprint,
                        nickname=desc.nickname,
                        country_code=desc.country_code or 'Unknown',
                        ip_address=desc.address,
                        bandwidth=desc.bandwidth or 0,
                        flags=list(desc.flags),
                        is_stable='Stable' in desc.flags,
                        is_fast='Fast' in desc.flags,
                        is_guard='Guard' in desc.flags
                    )
                    exit_nodes.append(node)
                    
        except Exception as e:
            logger.error(f"Failed to get exit nodes: {e}")
            
        return sorted(exit_nodes, key=lambda x: x.bandwidth, reverse=True)
        
    def new_identity(self) -> bool:
        """Request new TOR identity"""
        if not self.is_connected:
            return False
            
        try:
            self.controller.signal(Signal.NEWNYM)
            logger.info("New TOR identity requested")
            return True
        except Exception as e:
            logger.error(f"Failed to request new identity: {e}")
            return False
            
    def test_connection(self, url: str = "https://check.torproject.org/api/ip") -> Dict[str, Any]:
        """Test TOR connection"""
        try:
            # Configure SOCKS proxy
            socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", self.socks_port)
            socket.socket = socks.socksocket
            
            response = requests.get(url, timeout=30)
            data = response.json()
            
            return {
                'success': True,
                'is_tor': data.get('IsTor', False),
                'ip': data.get('IP'),
                'country': data.get('Country')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            # Reset socket
            socket.socket = socket._original_socket

class TORFailureHandler:
    """Handle TOR circuit failures and recovery"""
    
    def __init__(self, tor_controller: TORController):
        self.tor_controller = tor_controller
        self.failure_counts = {}
        self.blacklisted_exits = set()
        self.max_failures = 3
        
    def handle_circuit_failure(self, circuit_id: str, config: CircuitConfig) -> Optional[str]:
        """Handle circuit failure and attempt recovery"""
        logger.warning(f"Handling failure for circuit {circuit_id}")
        
        # Get circuit info to identify problematic nodes
        try:
            circuit = self.tor_controller.controller.get_circuit(circuit_id)
            if circuit and circuit.path:
                exit_node = circuit.path[-1].fingerprint
                self.failure_counts[exit_node] = self.failure_counts.get(exit_node, 0) + 1
                
                # Blacklist problematic exit nodes
                if self.failure_counts[exit_node] >= self.max_failures:
                    self.blacklisted_exits.add(exit_node)
                    logger.info(f"Blacklisted exit node {exit_node} after {self.max_failures} failures")
                    
        except Exception as e:
            logger.error(f"Error analyzing failed circuit: {e}")
            
        # Create new circuit avoiding problematic nodes
        new_config = self._modify_config_for_retry(config)
        return self.tor_controller.create_circuit(new_config)
        
    def _modify_config_for_retry(self, config: CircuitConfig) -> CircuitConfig:
        """Modify circuit configuration for retry"""
        new_config = CircuitConfig(**asdict(config))
        
        # Remove blacklisted exit nodes
        if new_config.exit_nodes:
            new_config.exit_nodes = [
                node for node in new_config.exit_nodes 
                if node not in self.blacklisted_exits
            ]
            
        # Add randomization to avoid same path
        if new_config.require_countries:
            # Randomize country selection
            random.shuffle(new_config.require_countries)
            
        return new_config

class TORManager(QThread):
    """Thread-based TOR manager"""
    
    connection_changed = pyqtSignal(bool)
    circuit_created = pyqtSignal(str, dict)
    circuit_failed = pyqtSignal(str, str)
    status_updated = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.tor_controller = TORController()
        self.failure_handler = TORFailureHandler(self.tor_controller)
        self.auto_recovery = True
        
    def connect_tor(self, control_port: int = 9051, password: Optional[str] = None):
        """Connect to TOR network"""
        success = self.tor_controller.connect(control_port, password)
        self.connection_changed.emit(success)
        
        if success:
            self.status_updated.emit("Connected to TOR network")
        else:
            self.status_updated.emit("Failed to connect to TOR network")
            
    def disconnect_tor(self):
        """Disconnect from TOR network"""
        self.tor_controller.disconnect()
        self.connection_changed.emit(False)
        self.status_updated.emit("Disconnected from TOR network")

class TORWidget(QWidget):
    """TOR configuration and control widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tor_manager = TORManager()
        self.exit_nodes = []
        self.active_circuits = {}
        
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        """Setup TOR widget UI"""
        layout = QVBoxLayout(self)
        
        # Connection group
        connection_group = QGroupBox("TOR Connection")
        connection_layout = QGridLayout(connection_group)
        
        connection_layout.addWidget(QLabel("Control Port:"), 0, 0)
        self.control_port_spin = QSpinBox()
        self.control_port_spin.setRange(1024, 65535)
        self.control_port_spin.setValue(9051)
        connection_layout.addWidget(self.control_port_spin, 0, 1)
        
        connection_layout.addWidget(QLabel("SOCKS Port:"), 1, 0)
        self.socks_port_spin = QSpinBox()
        self.socks_port_spin.setRange(1024, 65535)
        self.socks_port_spin.setValue(9050)
        connection_layout.addWidget(self.socks_port_spin, 1, 1)
        
        self.connect_btn = QPushButton("Connect")
        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.setEnabled(False)
        
        connection_layout.addWidget(self.connect_btn, 0, 2)
        connection_layout.addWidget(self.disconnect_btn, 1, 2)
        
        # Circuit configuration
        circuit_group = QGroupBox("Circuit Configuration")
        circuit_layout = QGridLayout(circuit_group)
        
        circuit_layout.addWidget(QLabel("Exit Country:"), 0, 0)
        self.exit_country_combo = QComboBox()
        self.exit_country_combo.addItems([
            "Any", "US", "DE", "NL", "FR", "UK", "CA", "SE", "CH", "AT"
        ])
        circuit_layout.addWidget(self.exit_country_combo, 0, 1)
        
        circuit_layout.addWidget(QLabel("Path Length:"), 1, 0)
        self.path_length_spin = QSpinBox()
        self.path_length_spin.setRange(2, 5)
        self.path_length_spin.setValue(3)
        circuit_layout.addWidget(self.path_length_spin, 1, 1)
        
        self.stable_only_cb = QCheckBox("Stable Nodes Only")
        self.stable_only_cb.setChecked(True)
        circuit_layout.addWidget(self.stable_only_cb, 2, 0)
        
        self.fast_only_cb = QCheckBox("Fast Nodes Only")
        self.fast_only_cb.setChecked(True)
        circuit_layout.addWidget(self.fast_only_cb, 2, 1)
        
        # Circuit controls
        controls_layout = QHBoxLayout()
        self.create_circuit_btn = QPushButton("Create Circuit")
        self.new_identity_btn = QPushButton("New Identity")
        self.test_connection_btn = QPushButton("Test Connection")
        
        controls_layout.addWidget(self.create_circuit_btn)
        controls_layout.addWidget(self.new_identity_btn)
        controls_layout.addWidget(self.test_connection_btn)
        controls_layout.addStretch()
        
        # Circuit table
        self.circuit_table = QTableWidget()
        self.circuit_table.setColumnCount(5)
        self.circuit_table.setHorizontalHeaderLabels([
            "Circuit ID", "Status", "Path", "Purpose", "Actions"
        ])
        
        # Exit nodes list
        exit_nodes_group = QGroupBox("Available Exit Nodes")
        exit_nodes_layout = QVBoxLayout(exit_nodes_group)
        
        self.refresh_nodes_btn = QPushButton("Refresh Exit Nodes")
        self.exit_nodes_list = QListWidget()
        
        exit_nodes_layout.addWidget(self.refresh_nodes_btn)
        exit_nodes_layout.addWidget(self.exit_nodes_list)
        
        # Status
        self.status_label = QLabel("Status: Disconnected")
        self.status_label.setStyleSheet("color: red;")
        
        # Layout
        layout.addWidget(connection_group)
        layout.addWidget(circuit_group)
        layout.addLayout(controls_layout)
        layout.addWidget(self.circuit_table)
        layout.addWidget(exit_nodes_group)
        layout.addWidget(self.status_label)
        
    def connect_signals(self):
        """Connect UI signals"""
        self.connect_btn.clicked.connect(self.connect_tor)
        self.disconnect_btn.clicked.connect(self.disconnect_tor)
        self.create_circuit_btn.clicked.connect(self.create_circuit)
        self.new_identity_btn.clicked.connect(self.new_identity)
        self.test_connection_btn.clicked.connect(self.test_connection)
        self.refresh_nodes_btn.clicked.connect(self.refresh_exit_nodes)
        
        # TOR manager signals
        self.tor_manager.connection_changed.connect(self.on_connection_changed)
        self.tor_manager.status_updated.connect(self.on_status_updated)
        
    def connect_tor(self):
        """Connect to TOR"""
        control_port = self.control_port_spin.value()
        self.tor_manager.connect_tor(control_port)
        
    def disconnect_tor(self):
        """Disconnect from TOR"""
        self.tor_manager.disconnect_tor()
        
    def create_circuit(self):
        """Create new TOR circuit"""
        if not self.tor_manager.tor_controller.is_connected:
            return
            
        # Build circuit configuration
        config = CircuitConfig(
            path_length=self.path_length_spin.value()
        )
        
        # Set country preference
        country = self.exit_country_combo.currentText()
        if country != "Any":
            config.require_countries = [country]
            
        # Create circuit
        circuit_id = self.tor_manager.tor_controller.create_circuit(config)
        if circuit_id:
            self.status_label.setText(f"Created circuit {circuit_id}")
            self.refresh_circuits()
        else:
            self.status_label.setText("Failed to create circuit")
            
    def new_identity(self):
        """Request new TOR identity"""
        if self.tor_manager.tor_controller.new_identity():
            self.status_label.setText("New identity requested")
        else:
            self.status_label.setText("Failed to request new identity")
            
    def test_connection(self):
        """Test TOR connection"""
        result = self.tor_manager.tor_controller.test_connection()
        
        if result['success']:
            if result['is_tor']:
                self.status_label.setText(f"TOR working - IP: {result['ip']} ({result.get('country', 'Unknown')})")
                self.status_label.setStyleSheet("color: green;")
            else:
                self.status_label.setText(f"Not using TOR - IP: {result['ip']}")
                self.status_label.setStyleSheet("color: orange;")
        else:
            self.status_label.setText(f"Connection test failed: {result.get('error', 'Unknown error')}")
            self.status_label.setStyleSheet("color: red;")
            
    def refresh_exit_nodes(self):
        """Refresh available exit nodes"""
        if not self.tor_manager.tor_controller.is_connected:
            return
            
        country = self.exit_country_combo.currentText()
        countries = [country] if country != "Any" else None
        
        self.exit_nodes = self.tor_manager.tor_controller.get_exit_nodes(countries)
        
        self.exit_nodes_list.clear()
        for node in self.exit_nodes[:50]:  # Show top 50
            item_text = f"{node.nickname} ({node.country_code}) - {node.bandwidth/1024/1024:.1f} MB/s"
            self.exit_nodes_list.addItem(item_text)
            
    def refresh_circuits(self):
        """Refresh circuit table"""
        if not self.tor_manager.tor_controller.is_connected:
            return
            
        circuits = self.tor_manager.tor_controller.get_circuits()
        
        self.circuit_table.setRowCount(len(circuits))
        
        for row, circuit in enumerate(circuits):
            self.circuit_table.setItem(row, 0, QTableWidgetItem(circuit['id']))
            self.circuit_table.setItem(row, 1, QTableWidgetItem(circuit['status']))
            self.circuit_table.setItem(row, 2, QTableWidgetItem(" → ".join(circuit['path'])))
            self.circuit_table.setItem(row, 3, QTableWidgetItem(circuit['purpose']))
            
            # Add close button
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(lambda checked, cid=circuit['id']: self.close_circuit(cid))
            self.circuit_table.setCellWidget(row, 4, close_btn)
            
    def close_circuit(self, circuit_id: str):
        """Close specific circuit"""
        if self.tor_manager.tor_controller.close_circuit(circuit_id):
            self.status_label.setText(f"Closed circuit {circuit_id}")
            self.refresh_circuits()
        else:
            self.status_label.setText(f"Failed to close circuit {circuit_id}")
            
    def on_connection_changed(self, connected: bool):
        """Handle TOR connection state change"""
        self.connect_btn.setEnabled(not connected)
        self.disconnect_btn.setEnabled(connected)
        self.create_circuit_btn.setEnabled(connected)
        self.new_identity_btn.setEnabled(connected)
        self.test_connection_btn.setEnabled(connected)
        self.refresh_nodes_btn.setEnabled(connected)
        
        if connected:
            self.status_label.setText("Status: Connected to TOR")
            self.status_label.setStyleSheet("color: green;")
            # Auto-refresh on connection
            QTimer.singleShot(1000, self.refresh_circuits)
            QTimer.singleShot(2000, self.refresh_exit_nodes)
        else:
            self.status_label.setText("Status: Disconnected")
            self.status_label.setStyleSheet("color: red;")
            
    def on_status_updated(self, status: str):
        """Handle status updates"""
        self.status_label.setText(f"Status: {status}")
        
    def get_tor_proxy_config(self) -> Dict[str, Any]:
        """Get TOR proxy configuration for scrapers"""
        return {
            'proxy_type': 'socks5',
            'proxy_host': '127.0.0.1',
            'proxy_port': self.socks_port_spin.value(),
            'enabled': self.tor_manager.tor_controller.is_connected
        }
