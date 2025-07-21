"""
Advanced Entity Graph Widget

Interactive GUI component for the Advanced Entity Graph System providing
comprehensive graph visualization, analytics, and investigation tools.
"""

import logging
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
import json

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QGroupBox, 
    QLabel, QPushButton, QComboBox, QSpinBox, QSlider, QCheckBox,
    QTableWidget, QTableWidgetItem, QTreeWidget, QTreeWidgetItem,
    QTextEdit, QProgressBar, QSplitter, QFrame, QScrollArea,
    QLineEdit, QListWidget, QListWidgetItem, QFormLayout, QDialog,
    QDialogButtonBox, QTextBrowser, QApplication, QMessageBox,
    QGridLayout, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize, QUrl, qApp
from PyQt6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QPixmap, QIcon,
    QPalette, QTextCursor, QDesktopServices
)
from PyQt6.QtWebEngineWidgets import QWebEngineView

from .advanced_entity_graph import (
    AdvancedEntityGraphSystem, NodeType, RelationshipType, GraphDatabase,
    EntityNode, EntityRelationship, GraphAnalytics, advanced_entity_graph
)

logger = logging.getLogger(__name__)


class GraphAnalyticsThread(QThread):
    """Background thread for graph analytics operations"""
    
    analytics_completed = pyqtSignal(object)  # GraphAnalytics
    progress_updated = pyqtSignal(str, int)  # status, percentage
    error_occurred = pyqtSignal(str)
    
    def __init__(self, graph_system: AdvancedEntityGraphSystem):
        super().__init__()
        self.graph_system = graph_system
        self.operation = None
        self.parameters = {}
    
    def set_operation(self, operation: str, **kwargs):
        """Set the operation to perform"""
        self.operation = operation
        self.parameters = kwargs
    
    def run(self):
        """Execute the analytics operation"""
        try:
            if self.operation == 'full_analytics':
                self.progress_updated.emit("Starting comprehensive analytics...", 10)
                
                # Run analytics asynchronously
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                self.progress_updated.emit("Calculating centrality measures...", 30)
                analytics = loop.run_until_complete(self.graph_system.perform_analytics())
                
                self.progress_updated.emit("Analytics completed", 100)
                self.analytics_completed.emit(analytics)
                
                loop.close()
                
            elif self.operation == 'query':
                self.progress_updated.emit("Executing query...", 50)
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                query = self.parameters.get('query', '')
                params = self.parameters.get('parameters', {})
                
                results = loop.run_until_complete(
                    self.graph_system.query_graph(query, params)
                )
                
                self.progress_updated.emit("Query completed", 100)
                self.analytics_completed.emit(results)
                
                loop.close()
                
        except Exception as e:
            self.error_occurred.emit(str(e))


class EntityAddDialog(QDialog):
    """Dialog for adding new entities to the graph"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Entity")
        self.setModal(True)
        self.resize(400, 300)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Entity ID
        self.entity_id_edit = QLineEdit()
        self.entity_id_edit.setPlaceholderText("Unique entity identifier")
        form_layout.addRow("Entity ID:", self.entity_id_edit)
        
        # Node type
        self.node_type_combo = QComboBox()
        self.node_type_combo.addItems([node_type.value for node_type in NodeType])
        form_layout.addRow("Type:", self.node_type_combo)
        
        # Name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Display name")
        form_layout.addRow("Name:", self.name_edit)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText("Optional description")
        form_layout.addRow("Description:", self.description_edit)
        
        # Confidence
        self.confidence_slider = QSlider(Qt.Orientation.Horizontal)
        self.confidence_slider.setRange(0, 100)
        self.confidence_slider.setValue(100)
        self.confidence_label = QLabel("1.00")
        
        confidence_layout = QHBoxLayout()
        confidence_layout.addWidget(self.confidence_slider)
        confidence_layout.addWidget(self.confidence_label)
        
        self.confidence_slider.valueChanged.connect(
            lambda v: self.confidence_label.setText(f"{v/100:.2f}")
        )
        
        form_layout.addRow("Confidence:", confidence_layout)
        
        # Data source
        self.data_source_edit = QLineEdit()
        self.data_source_edit.setPlaceholderText("Source of this entity data")
        form_layout.addRow("Data Source:", self.data_source_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_entity_data(self) -> Dict[str, Any]:
        """Get the entity data from the form"""
        properties = {}
        if self.name_edit.text():
            properties['name'] = self.name_edit.text()
        if self.description_edit.toPlainText():
            properties['description'] = self.description_edit.toPlainText()
        
        data_sources = []
        if self.data_source_edit.text():
            data_sources.append(self.data_source_edit.text())
        
        return {
            'entity_id': self.entity_id_edit.text(),
            'node_type': NodeType(self.node_type_combo.currentText()),
            'properties': properties,
            'confidence': self.confidence_slider.value() / 100.0,
            'data_sources': data_sources
        }


class RelationshipAddDialog(QDialog):
    """Dialog for adding relationships between entities"""
    
    def __init__(self, entity_ids: List[str], parent=None):
        super().__init__(parent)
        self.entity_ids = entity_ids
        self.setWindowTitle("Add Relationship")
        self.setModal(True)
        self.resize(450, 350)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Source entity
        self.source_combo = QComboBox()
        self.source_combo.addItems(self.entity_ids)
        self.source_combo.setEditable(True)
        form_layout.addRow("Source Entity:", self.source_combo)
        
        # Target entity
        self.target_combo = QComboBox()
        self.target_combo.addItems(self.entity_ids)
        self.target_combo.setEditable(True)
        form_layout.addRow("Target Entity:", self.target_combo)
        
        # Relationship type
        self.relationship_type_combo = QComboBox()
        self.relationship_type_combo.addItems([rel_type.value for rel_type in RelationshipType])
        form_layout.addRow("Relationship Type:", self.relationship_type_combo)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(60)
        self.description_edit.setPlaceholderText("Optional relationship description")
        form_layout.addRow("Description:", self.description_edit)
        
        # Confidence
        self.confidence_slider = QSlider(Qt.Orientation.Horizontal)
        self.confidence_slider.setRange(0, 100)
        self.confidence_slider.setValue(100)
        self.confidence_label = QLabel("1.00")
        
        confidence_layout = QHBoxLayout()
        confidence_layout.addWidget(self.confidence_slider)
        confidence_layout.addWidget(self.confidence_label)
        
        self.confidence_slider.valueChanged.connect(
            lambda v: self.confidence_label.setText(f"{v/100:.2f}")
        )
        
        form_layout.addRow("Confidence:", confidence_layout)
        
        # Temporal validity
        self.valid_from_edit = QLineEdit()
        self.valid_from_edit.setPlaceholderText("YYYY-MM-DD (optional)")
        form_layout.addRow("Valid From:", self.valid_from_edit)
        
        self.valid_to_edit = QLineEdit()
        self.valid_to_edit.setPlaceholderText("YYYY-MM-DD (optional)")
        form_layout.addRow("Valid To:", self.valid_to_edit)
        
        # Data source
        self.data_source_edit = QLineEdit()
        self.data_source_edit.setPlaceholderText("Source of this relationship data")
        form_layout.addRow("Data Source:", self.data_source_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_relationship_data(self) -> Dict[str, Any]:
        """Get the relationship data from the form"""
        properties = {}
        if self.description_edit.toPlainText():
            properties['description'] = self.description_edit.toPlainText()
        
        data_sources = []
        if self.data_source_edit.text():
            data_sources.append(self.data_source_edit.text())
        
        # Parse dates
        valid_from = None
        valid_to = None
        
        try:
            if self.valid_from_edit.text():
                valid_from = datetime.strptime(self.valid_from_edit.text(), "%Y-%m-%d")
                valid_from = valid_from.replace(tzinfo=timezone.utc)
        except ValueError:
            pass
        
        try:
            if self.valid_to_edit.text():
                valid_to = datetime.strptime(self.valid_to_edit.text(), "%Y-%m-%d")
                valid_to = valid_to.replace(tzinfo=timezone.utc)
        except ValueError:
            pass
        
        return {
            'source_id': self.source_combo.currentText(),
            'target_id': self.target_combo.currentText(),
            'relationship_type': RelationshipType(self.relationship_type_combo.currentText()),
            'properties': properties,
            'confidence': self.confidence_slider.value() / 100.0,
            'valid_from': valid_from,
            'valid_to': valid_to,
            'data_sources': data_sources
        }


class AdvancedEntityGraphWidget(QWidget):
    """Main widget for the Advanced Entity Graph System"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.graph_system = advanced_entity_graph
        self.analytics_thread = None
        self.current_analytics: Optional[GraphAnalytics] = None
        
        self.setup_ui()
        self.setup_connections()
        
        # Initialize with default settings
        QTimer.singleShot(100, self.initialize_graph_system)
    
    def setup_ui(self):
        """Setup the widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Advanced Entity Graph System")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Database connection controls
        self.db_type_combo = QComboBox()
        self.db_type_combo.addItems([db.value for db in GraphDatabase])
        self.db_type_combo.setCurrentText(GraphDatabase.NETWORKX.value)
        header_layout.addWidget(QLabel("Database:"))
        header_layout.addWidget(self.db_type_combo)
        
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setStyleSheet("padding: 5px 10px; font-weight: bold;")
        header_layout.addWidget(self.connect_btn)
        
        layout.addLayout(header_layout)
        
        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        layout.addWidget(self.status_label)
        
        # Main content
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(main_splitter)
        
        # Left panel - Controls and Analysis
        left_panel = self.create_left_panel()
        main_splitter.addWidget(left_panel)
        
        # Right panel - Visualization and Results
        right_panel = self.create_right_panel()
        main_splitter.addWidget(right_panel)
        
        # Set splitter proportions
        main_splitter.setSizes([400, 600])
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
    
    def create_left_panel(self) -> QWidget:
        """Create the left control panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Graph Management
        graph_group = QGroupBox("Graph Management")
        graph_layout = QVBoxLayout(graph_group)
        
        # Entity management
        entity_layout = QHBoxLayout()
        self.add_entity_btn = QPushButton("Add Entity")
        self.add_relationship_btn = QPushButton("Add Relationship")
        entity_layout.addWidget(self.add_entity_btn)
        entity_layout.addWidget(self.add_relationship_btn)
        graph_layout.addLayout(entity_layout)
        
        # Import/Export
        io_layout = QHBoxLayout()
        self.import_btn = QPushButton("Import Data")
        self.export_btn = QPushButton("Export Graph")
        io_layout.addWidget(self.import_btn)
        io_layout.addWidget(self.export_btn)
        graph_layout.addLayout(io_layout)
        
        layout.addWidget(graph_group)
        
        # Analytics Controls
        analytics_group = QGroupBox("Graph Analytics")
        analytics_layout = QVBoxLayout(analytics_group)
        
        self.run_analytics_btn = QPushButton("Run Full Analytics")
        self.run_analytics_btn.setStyleSheet("padding: 8px; font-weight: bold; background-color: #3498db; color: white;")
        analytics_layout.addWidget(self.run_analytics_btn)
        
        # Quick analytics buttons
        quick_layout = QGridLayout()
        
        self.centrality_btn = QPushButton("Centrality")
        self.communities_btn = QPushButton("Communities")
        self.anomalies_btn = QPushButton("Anomalies")
        self.temporal_btn = QPushButton("Temporal")
        
        quick_layout.addWidget(self.centrality_btn, 0, 0)
        quick_layout.addWidget(self.communities_btn, 0, 1)
        quick_layout.addWidget(self.anomalies_btn, 1, 0)
        quick_layout.addWidget(self.temporal_btn, 1, 1)
        
        analytics_layout.addLayout(quick_layout)
        
        layout.addWidget(analytics_group)
        
        # Query Interface
        query_group = QGroupBox("Graph Queries")
        query_layout = QVBoxLayout(query_group)
        
        # Query templates
        self.query_template_combo = QComboBox()
        self.query_template_combo.addItems([
            "Custom Query",
            "Circular Ownership",
            "Directors in Common", 
            "Ultimate Beneficial Owners",
            "Shell Company Detection",
            "Network Expansion",
            "Risk Propagation"
        ])
        query_layout.addWidget(QLabel("Template:"))
        query_layout.addWidget(self.query_template_combo)
        
        # Query input
        self.query_edit = QTextEdit()
        self.query_edit.setMaximumHeight(100)
        self.query_edit.setPlaceholderText("Enter Cypher query or use template...")
        query_layout.addWidget(QLabel("Query:"))
        query_layout.addWidget(self.query_edit)
        
        # Parameters
        self.params_edit = QLineEdit()
        self.params_edit.setPlaceholderText('{"entity_id": "example"} (JSON)')
        query_layout.addWidget(QLabel("Parameters:"))
        query_layout.addWidget(self.params_edit)
        
        self.execute_query_btn = QPushButton("Execute Query")
        query_layout.addWidget(self.execute_query_btn)
        
        layout.addWidget(query_group)
        
        # Visualization Controls
        viz_group = QGroupBox("Visualization")
        viz_layout = QFormLayout(viz_group)
        
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(['spring', 'circular', 'hierarchical', 'fruchterman_reingold'])
        viz_layout.addRow("Layout:", self.layout_combo)
        
        self.color_combo = QComboBox()
        self.color_combo.addItems(['node_type', 'centrality', 'confidence', 'community'])
        viz_layout.addRow("Color By:", self.color_combo)
        
        self.show_labels_check = QCheckBox()
        self.show_labels_check.setChecked(True)
        viz_layout.addRow("Show Labels:", self.show_labels_check)
        
        self.update_viz_btn = QPushButton("Update Visualization")
        viz_layout.addWidget(self.update_viz_btn)
        
        layout.addWidget(viz_group)
        
        layout.addStretch()
        
        return panel
    
    def create_right_panel(self) -> QWidget:
        """Create the right results panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Tabbed interface
        self.tab_widget = QTabWidget()
        
        # Visualization tab
        viz_tab = QWidget()
        viz_layout = QVBoxLayout(viz_tab)
        
        try:
            self.web_view = QWebEngineView()
            self.web_view.setMinimumHeight(400)
            viz_layout.addWidget(self.web_view)
        except ImportError:
            # Fallback if QWebEngineView not available
            self.viz_placeholder = QTextBrowser()
            self.viz_placeholder.setHtml("<h3>Visualization</h3><p>Graph visualization will appear here.</p>")
            viz_layout.addWidget(self.viz_placeholder)
        
        self.tab_widget.addTab(viz_tab, "Graph Visualization")
        
        # Analytics Results tab
        analytics_tab = QWidget()
        analytics_layout = QVBoxLayout(analytics_tab)
        
        self.analytics_text = QTextBrowser()
        self.analytics_text.setPlaceholderText("Analytics results will appear here...")
        analytics_layout.addWidget(self.analytics_text)
        
        self.tab_widget.addTab(analytics_tab, "Analytics Results")
        
        # Entity List tab
        entities_tab = QWidget()
        entities_layout = QVBoxLayout(entities_tab)
        
        self.entities_table = QTableWidget()
        self.entities_table.setColumnCount(4)
        self.entities_table.setHorizontalHeaderLabels(["ID", "Type", "Name", "Confidence"])
        entities_layout.addWidget(self.entities_table)
        
        self.tab_widget.addTab(entities_tab, "Entities")
        
        # Relationships tab
        relationships_tab = QWidget()
        relationships_layout = QVBoxLayout(relationships_tab)
        
        self.relationships_table = QTableWidget()
        self.relationships_table.setColumnCount(4)
        self.relationships_table.setHorizontalHeaderLabels(["Source", "Target", "Type", "Confidence"])
        relationships_layout.addWidget(self.relationships_table)
        
        self.tab_widget.addTab(relationships_tab, "Relationships")
        
        # Query Results tab
        query_results_tab = QWidget()
        query_results_layout = QVBoxLayout(query_results_tab)
        
        self.query_results_text = QTextBrowser()
        self.query_results_text.setPlaceholderText("Query results will appear here...")
        query_results_layout.addWidget(self.query_results_text)
        
        self.tab_widget.addTab(query_results_tab, "Query Results")
        
        layout.addWidget(self.tab_widget)
        
        return panel
    
    def setup_connections(self):
        """Setup signal connections"""
        self.connect_btn.clicked.connect(self.connect_to_database)
        self.add_entity_btn.clicked.connect(self.add_entity_dialog)
        self.add_relationship_btn.clicked.connect(self.add_relationship_dialog)
        self.run_analytics_btn.clicked.connect(self.run_full_analytics)
        self.execute_query_btn.clicked.connect(self.execute_query)
        self.update_viz_btn.clicked.connect(self.update_visualization)
        
        # Quick analytics buttons
        self.centrality_btn.clicked.connect(lambda: self.run_quick_analytics('centrality'))
        self.communities_btn.clicked.connect(lambda: self.run_quick_analytics('communities'))
        self.anomalies_btn.clicked.connect(lambda: self.run_quick_analytics('anomalies'))
        self.temporal_btn.clicked.connect(lambda: self.run_quick_analytics('temporal'))
        
        # Query template selection
        self.query_template_combo.currentTextChanged.connect(self.load_query_template)
    
    def initialize_graph_system(self):
        """Initialize the graph system"""
        asyncio.create_task(self.async_initialize())
    
    async def async_initialize(self):
        """Asynchronously initialize the graph system"""
        try:
            success = await self.graph_system.initialize(GraphDatabase.NETWORKX)
            if success:
                self.status_label.setText("Graph system initialized")
                self.update_entity_list()
                self.update_relationship_list()
            else:
                self.status_label.setText("Failed to initialize graph system")
        except Exception as e:
            self.status_label.setText(f"Initialization error: {str(e)}")
            logger.error(f"Graph system initialization error: {e}")
    
    def connect_to_database(self):
        """Connect to the selected database"""
        db_type = GraphDatabase(self.db_type_combo.currentText())
        
        if db_type == GraphDatabase.NEO4J:
            # Show connection dialog for Neo4j
            QMessageBox.information(
                self, 
                "Neo4j Connection", 
                "Neo4j connection dialog would appear here.\nFor now, using NetworkX in-memory database."
            )
            return
        
        # Initialize with selected database type
        asyncio.create_task(self.reconnect_database(db_type))
    
    async def reconnect_database(self, db_type: GraphDatabase):
        """Reconnect to database with new type"""
        try:
            await self.graph_system.shutdown()
            success = await self.graph_system.initialize(db_type)
            
            if success:
                self.status_label.setText(f"Connected to {db_type.value}")
                self.update_entity_list()
                self.update_relationship_list()
            else:
                self.status_label.setText(f"Failed to connect to {db_type.value}")
        except Exception as e:
            self.status_label.setText(f"Connection error: {str(e)}")
    
    def add_entity_dialog(self):
        """Show add entity dialog"""
        dialog = EntityAddDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            entity_data = dialog.get_entity_data()
            asyncio.create_task(self.add_entity_async(entity_data))
    
    async def add_entity_async(self, entity_data: Dict[str, Any]):
        """Add entity asynchronously"""
        try:
            success = await self.graph_system.add_entity(**entity_data)
            if success:
                self.status_label.setText(f"Added entity: {entity_data['entity_id']}")
                self.update_entity_list()
                self.update_visualization()
            else:
                self.status_label.setText("Failed to add entity")
        except Exception as e:
            self.status_label.setText(f"Error adding entity: {str(e)}")
    
    def add_relationship_dialog(self):
        """Show add relationship dialog"""
        # Get current entity IDs
        entity_ids = []
        if hasattr(self.graph_system.connector, 'nodes_data'):
            entity_ids = list(self.graph_system.connector.nodes_data.keys())
        
        if len(entity_ids) < 2:
            QMessageBox.warning(
                self, 
                "Insufficient Entities", 
                "You need at least 2 entities to create a relationship."
            )
            return
        
        dialog = RelationshipAddDialog(entity_ids, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            relationship_data = dialog.get_relationship_data()
            asyncio.create_task(self.add_relationship_async(relationship_data))
    
    async def add_relationship_async(self, relationship_data: Dict[str, Any]):
        """Add relationship asynchronously"""
        try:
            success = await self.graph_system.add_relationship(**relationship_data)
            if success:
                self.status_label.setText(f"Added relationship: {relationship_data['relationship_type'].value}")
                self.update_relationship_list()
                self.update_visualization()
            else:
                self.status_label.setText("Failed to add relationship")
        except Exception as e:
            self.status_label.setText(f"Error adding relationship: {str(e)}")
    
    def run_full_analytics(self):
        """Run comprehensive graph analytics"""
        if self.analytics_thread and self.analytics_thread.isRunning():
            return
        
        self.analytics_thread = GraphAnalyticsThread(self.graph_system)
        self.analytics_thread.analytics_completed.connect(self.on_analytics_completed)
        self.analytics_thread.progress_updated.connect(self.on_progress_updated)
        self.analytics_thread.error_occurred.connect(self.on_analytics_error)
        
        self.analytics_thread.set_operation('full_analytics')
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.run_analytics_btn.setEnabled(False)
        
        self.analytics_thread.start()
    
    def run_quick_analytics(self, analysis_type: str):
        """Run specific analytics"""
        self.status_label.setText(f"Running {analysis_type} analysis...")
        # Implementation would depend on specific analysis type
        QTimer.singleShot(1000, lambda: self.status_label.setText(f"{analysis_type.title()} analysis completed"))
    
    def execute_query(self):
        """Execute graph query"""
        query = self.query_edit.toPlainText().strip()
        if not query:
            return
        
        # Parse parameters
        parameters = {}
        try:
            params_text = self.params_edit.text().strip()
            if params_text:
                parameters = json.loads(params_text)
        except json.JSONDecodeError:
            self.status_label.setText("Invalid JSON in parameters")
            return
        
        if self.analytics_thread and self.analytics_thread.isRunning():
            return
        
        self.analytics_thread = GraphAnalyticsThread(self.graph_system)
        self.analytics_thread.analytics_completed.connect(self.on_query_completed)
        self.analytics_thread.progress_updated.connect(self.on_progress_updated)
        self.analytics_thread.error_occurred.connect(self.on_analytics_error)
        
        self.analytics_thread.set_operation('query', query=query, parameters=parameters)
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.execute_query_btn.setEnabled(False)
        
        self.analytics_thread.start()
    
    def load_query_template(self, template_name: str):
        """Load a query template"""
        templates = {
            "Circular Ownership": """
MATCH path = (c1:COMPANY)-[:OWNS*2..5]->(c1)
WHERE c1.entity_id = $entity_id
RETURN path
            """,
            "Directors in Common": """
MATCH (p:PERSON)-[:HAS_OFFICER]->(c1:COMPANY)
MATCH (p)-[:HAS_OFFICER]->(c2:COMPANY)
WHERE c1 <> c2 AND c1.entity_id = $entity_id
RETURN p, c1, c2
            """,
            "Ultimate Beneficial Owners": """
MATCH path = (start:COMPANY)-[:OWNS*]->(end:PERSON)
WHERE start.entity_id = $entity_id
AND NOT (end)-[:OWNS]->()
RETURN path ORDER BY length(path) DESC LIMIT 10
            """,
            "Shell Company Detection": """
MATCH (c:COMPANY)
WHERE c.entity_id = $entity_id
OPTIONAL MATCH (c)-[:HAS_OFFICER]->(officers)
OPTIONAL MATCH (c)-[:REGISTERED_AT]->(addr:ADDRESS)
WITH c, count(officers) as officer_count, collect(addr) as addresses
WHERE officer_count <= 1 OR size(addresses) = 0
RETURN c, officer_count, addresses
            """,
            "Network Expansion": """
MATCH (start {entity_id: $entity_id})
MATCH path = (start)-[*1..$max_hops]-(connected)
RETURN path, connected
ORDER BY length(path)
LIMIT $limit
            """,
            "Risk Propagation": """
MATCH path = (risk_entity {entity_id: $entity_id})-[*1..$depth]-(connected)
WHERE any(rel in relationships(path) WHERE rel.confidence < 0.7)
RETURN path, connected
ORDER BY length(path)
            """
        }
        
        if template_name in templates:
            self.query_edit.setPlainText(templates[template_name].strip())
            
            # Set example parameters
            if template_name in ["Circular Ownership", "Directors in Common", "Ultimate Beneficial Owners", "Shell Company Detection"]:
                self.params_edit.setText('{"entity_id": "COMPANY_001"}')
            elif template_name == "Network Expansion":
                self.params_edit.setText('{"entity_id": "COMPANY_001", "max_hops": 3, "limit": 100}')
            elif template_name == "Risk Propagation":
                self.params_edit.setText('{"entity_id": "COMPANY_001", "depth": 2}')
    
    def update_visualization(self):
        """Update the graph visualization"""
        try:
            layout = self.layout_combo.currentText()
            color_by = self.color_combo.currentText()
            show_labels = self.show_labels_check.isChecked()
            
            html_content = self.graph_system.create_visualization(layout, color_by, show_labels)
            
            if html_content and hasattr(self, 'web_view'):
                self.web_view.setHtml(html_content)
            elif hasattr(self, 'viz_placeholder'):
                self.viz_placeholder.setHtml(
                    f"<h3>Graph Visualization</h3>"
                    f"<p>Layout: {layout}</p>"
                    f"<p>Color scheme: {color_by}</p>"
                    f"<p>Interactive visualization would appear here with WebEngine support.</p>"
                )
            
            self.status_label.setText("Visualization updated")
            
        except Exception as e:
            self.status_label.setText(f"Visualization error: {str(e)}")
            logger.error(f"Visualization error: {e}")
    
    def update_entity_list(self):
        """Update the entities table"""
        try:
            if not hasattr(self.graph_system.connector, 'nodes_data'):
                return
            
            nodes_data = self.graph_system.connector.nodes_data
            self.entities_table.setRowCount(len(nodes_data))
            
            for row, (entity_id, node) in enumerate(nodes_data.items()):
                self.entities_table.setItem(row, 0, QTableWidgetItem(entity_id))
                self.entities_table.setItem(row, 1, QTableWidgetItem(node.node_type.value))
                self.entities_table.setItem(row, 2, QTableWidgetItem(node.display_name))
                self.entities_table.setItem(row, 3, QTableWidgetItem(f"{node.confidence:.2f}"))
            
            self.entities_table.resizeColumnsToContents()
            
        except Exception as e:
            logger.error(f"Error updating entity list: {e}")
    
    def update_relationship_list(self):
        """Update the relationships table"""
        try:
            if not hasattr(self.graph_system.connector, 'relationships_data'):
                return
            
            relationships_data = self.graph_system.connector.relationships_data
            self.relationships_table.setRowCount(len(relationships_data))
            
            for row, (rel_key, relationship) in enumerate(relationships_data.items()):
                self.relationships_table.setItem(row, 0, QTableWidgetItem(relationship.source_id))
                self.relationships_table.setItem(row, 1, QTableWidgetItem(relationship.target_id))
                self.relationships_table.setItem(row, 2, QTableWidgetItem(relationship.relationship_type.value))
                self.relationships_table.setItem(row, 3, QTableWidgetItem(f"{relationship.confidence:.2f}"))
            
            self.relationships_table.resizeColumnsToContents()
            
        except Exception as e:
            logger.error(f"Error updating relationship list: {e}")
    
    def on_analytics_completed(self, analytics: GraphAnalytics):
        """Handle analytics completion"""
        self.current_analytics = analytics
        
        # Display results
        results_html = self.format_analytics_results(analytics)
        self.analytics_text.setHtml(results_html)
        
        # Switch to analytics tab
        self.tab_widget.setCurrentIndex(1)
        
        self.progress_bar.setVisible(False)
        self.run_analytics_btn.setEnabled(True)
        self.status_label.setText("Analytics completed")
    
    def on_query_completed(self, results: List[Dict[str, Any]]):
        """Handle query completion"""
        # Display query results
        results_html = self.format_query_results(results)
        self.query_results_text.setHtml(results_html)
        
        # Switch to query results tab
        self.tab_widget.setCurrentIndex(4)
        
        self.progress_bar.setVisible(False)
        self.execute_query_btn.setEnabled(True)
        self.status_label.setText("Query completed")
    
    def on_progress_updated(self, status: str, percentage: int):
        """Handle progress updates"""
        self.status_label.setText(status)
        self.progress_bar.setValue(percentage)
    
    def on_analytics_error(self, error_message: str):
        """Handle analytics errors"""
        self.progress_bar.setVisible(False)
        self.run_analytics_btn.setEnabled(True)
        self.execute_query_btn.setEnabled(True)
        self.status_label.setText(f"Error: {error_message}")
        
        QMessageBox.critical(self, "Analytics Error", error_message)
    
    def format_analytics_results(self, analytics: GraphAnalytics) -> str:
        """Format analytics results as HTML"""
        html = "<h2>Graph Analytics Results</h2>"
        
        # Centrality measures
        if analytics.centrality_measures:
            html += "<h3>Centrality Measures</h3>"
            html += "<table border='1' style='border-collapse: collapse; width: 100%;'>"
            html += "<tr><th>Node</th><th>Degree</th><th>Betweenness</th><th>PageRank</th></tr>"
            
            nodes = set()
            for measure_type in analytics.centrality_measures.values():
                nodes.update(measure_type.keys())
            
            for node in sorted(nodes):
                degree = analytics.centrality_measures.get('degree', {}).get(node, 0)
                betweenness = analytics.centrality_measures.get('betweenness', {}).get(node, 0)
                pagerank = analytics.centrality_measures.get('pagerank', {}).get(node, 0)
                
                html += f"<tr><td>{node}</td><td>{degree:.3f}</td><td>{betweenness:.3f}</td><td>{pagerank:.3f}</td></tr>"
            
            html += "</table>"
        
        # Community detection
        if analytics.community_detection:
            html += "<h3>Community Detection</h3>"
            html += "<p>Found communities:</p><ul>"
            
            communities = {}
            for node, community_id in analytics.community_detection.items():
                if community_id not in communities:
                    communities[community_id] = []
                communities[community_id].append(node)
            
            for community_id, nodes in communities.items():
                html += f"<li><strong>Community {community_id}:</strong> {', '.join(nodes)}</li>"
            
            html += "</ul>"
        
        # Anomalies
        if analytics.anomalies:
            html += "<h3>Detected Anomalies</h3>"
            html += "<ul>"
            
            for anomaly in analytics.anomalies:
                anomaly_type = anomaly.get('type', 'unknown')
                severity = anomaly.get('severity', 0)
                
                if anomaly_type == 'high_degree_node':
                    node_id = anomaly.get('node_id', 'unknown')
                    degree = anomaly.get('degree', 0)
                    html += f"<li><strong>High Degree Node:</strong> {node_id} (degree: {degree}, severity: {severity:.2f})</li>"
                elif anomaly_type == 'isolated_component':
                    nodes = anomaly.get('nodes', [])
                    html += f"<li><strong>Isolated Component:</strong> {len(nodes)} nodes, severity: {severity:.2f}</li>"
                else:
                    html += f"<li><strong>{anomaly_type.replace('_', ' ').title()}:</strong> severity: {severity:.2f}</li>"
            
            html += "</ul>"
        
        # Temporal analysis
        if analytics.temporal_analysis:
            html += "<h3>Temporal Analysis</h3>"
            
            growth_metrics = analytics.temporal_analysis.get('growth_metrics', {})
            if growth_metrics:
                html += "<h4>Growth Metrics</h4><ul>"
                for metric, value in growth_metrics.items():
                    html += f"<li><strong>{metric.replace('_', ' ').title()}:</strong> {value}</li>"
                html += "</ul>"
        
        # Network metrics
        if analytics.network_metrics:
            html += "<h3>Network Metrics</h3><ul>"
            for metric, value in analytics.network_metrics.items():
                html += f"<li><strong>{metric.replace('_', ' ').title()}:</strong> {value}</li>"
            html += "</ul>"
        
        return html
    
    def format_query_results(self, results: List[Dict[str, Any]]) -> str:
        """Format query results as HTML"""
        html = "<h2>Query Results</h2>"
        
        if not results:
            html += "<p>No results found.</p>"
            return html
        
        html += f"<p>Found {len(results)} result(s):</p>"
        
        html += "<table border='1' style='border-collapse: collapse; width: 100%;'>"
        
        # Header
        if results:
            headers = list(results[0].keys())
            html += "<tr>"
            for header in headers:
                html += f"<th>{header}</th>"
            html += "</tr>"
            
            # Data rows
            for result in results[:100]:  # Limit to first 100 results
                html += "<tr>"
                for header in headers:
                    value = result.get(header, '')
                    # Convert complex objects to string representation
                    if isinstance(value, (dict, list)):
                        value = json.dumps(value, default=str, indent=2)
                    html += f"<td>{str(value)}</td>"
                html += "</tr>"
        
        html += "</table>"
        
        if len(results) > 100:
            html += f"<p><em>Showing first 100 of {len(results)} results.</em></p>"
        
        return html
