"""
Data Visualization System with 2D/3D Site Mapping
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QGroupBox, QLabel, QPushButton, QComboBox, QCheckBox,
                            QSlider, QSpinBox, QTabWidget, QTextEdit, QListWidget,
                            QTreeWidget, QTreeWidgetItem, QSplitter, QProgressBar,
                            QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QPoint
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont
try:
    from PyQt6.QtOpenGLWidgets import QOpenGLWidget
    OPENGL_AVAILABLE = True
except ImportError:
    # Fallback for systems without OpenGL support
    OPENGL_AVAILABLE = False
    QOpenGLWidget = QWidget  # Use regular widget as fallback
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    nx = None
import json
import math
import random
import logging

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.offline as pyo
    import networkx as nx
    import numpy as np
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class SiteNode:
    """Represents a website node in the visualization"""
    url: str
    domain: str
    title: str = ""
    status_code: int = 200
    response_time: float = 0.0
    crawl_depth: int = 0
    links_found: int = 0
    data_extracted: int = 0
    last_crawled: Optional[datetime] = None
    coordinates: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    node_type: str = "page"  # page, domain, subdomain, external
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SiteLink:
    """Represents a link between sites"""
    source_url: str
    target_url: str
    link_type: str = "hyperlink"  # hyperlink, redirect, form, ajax
    weight: float = 1.0
    discovered_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class NetworkLayoutEngine:
    """Layout engine for positioning nodes in 2D/3D space"""
    
    def __init__(self, mode="2d"):
        self.mode = mode  # "2d" or "3d"
        self.nodes: Dict[str, SiteNode] = {}
        self.links: List[SiteLink] = []
        self.graph = None
        
        if NETWORKX_AVAILABLE and nx is not None:
            self.graph = nx.Graph()
    
    def add_node(self, node: SiteNode):
        """Add a node to the visualization"""
        self.nodes[node.url] = node
        if self.graph is not None and nx is not None:
            self.graph.add_node(
                node.url,
                title=node.title,
                domain=node.domain,
                status_code=node.status_code,
                response_time=node.response_time,
                crawl_depth=node.crawl_depth,
                node_type=node.node_type
            )
    
    def add_link(self, link: SiteLink):
        """Add a link between nodes"""
        self.links.append(link)
        if self.graph and link.source_url in self.nodes and link.target_url in self.nodes:
            self.graph.add_edge(
                link.source_url,
                link.target_url,
                weight=link.weight,
                link_type=link.link_type
            )
    
    def calculate_layout(self, algorithm="spring") -> Dict[str, Tuple[float, float, float]]:
        """Calculate node positions using specified algorithm"""
        if not self.graph or len(self.nodes) == 0 or nx is None:
            return self._fallback_layout()
        
        try:
            if algorithm == "spring":
                pos = nx.spring_layout(self.graph, dim=3 if self.mode == "3d" else 2, k=1.0, iterations=50)
            elif algorithm == "circular":
                pos = nx.circular_layout(self.graph)
                if self.mode == "3d":
                    # Add z-coordinate based on depth
                    for node_id in list(pos.keys()):  # Convert to list to avoid dict size change during iteration
                        depth = self.nodes[node_id].crawl_depth if node_id in self.nodes else 0
                        pos[node_id] = (*pos[node_id], depth * 0.1)
            elif algorithm == "hierarchical":
                pos = self._hierarchical_layout()
            elif algorithm == "force_directed":
                pos = self._force_directed_layout()
            else:
                pos = nx.random_layout(self.graph, dim=3 if self.mode == "3d" else 2)
            
            # Update node coordinates
            for node_url, coords in pos.items():
                if node_url in self.nodes:
                    if len(coords) == 2 and self.mode == "3d":
                        coords = (*coords, 0.0)
                    elif len(coords) == 3 and self.mode == "2d":
                        coords = coords[:2] + (0.0,)
                    self.nodes[node_url].coordinates = coords
            
            return pos
            
        except Exception as e:
            logger.error(f"Error calculating layout: {e}")
            return self._fallback_layout()
    
    def _hierarchical_layout(self) -> Dict[str, Tuple[float, float, float]]:
        """Create hierarchical layout based on crawl depth"""
        pos = {}
        depth_groups = {}
        
        # Group nodes by depth
        for node_url, node in self.nodes.items():
            depth = node.crawl_depth
            if depth not in depth_groups:
                depth_groups[depth] = []
            depth_groups[depth].append(node_url)
        
        # Position nodes in layers
        max_depth = max(depth_groups.keys()) if depth_groups else 0
        
        for depth, nodes in depth_groups.items():
            y = depth * 2.0  # Vertical spacing
            count = len(nodes)
            
            for i, node_url in enumerate(nodes):
                x = (i - count / 2) * 1.5  # Horizontal spacing
                z = 0.0 if self.mode == "2d" else random.uniform(-0.5, 0.5)
                pos[node_url] = (x, y, z)
        
        return pos
    
    def _force_directed_layout(self) -> Dict[str, Tuple[float, float, float]]:
        """Force-directed layout with custom physics"""
        if not NETWORKX_AVAILABLE or nx is None or self.graph is None:
            return self._fallback_layout()
        
        # Use NetworkX force-directed algorithm with custom parameters
        pos = nx.spring_layout(
            self.graph,
            dim=3 if self.mode == "3d" else 2,
            k=2.0,  # Optimal distance between nodes
            iterations=100,
            weight='weight'
        )
        
        return pos
    
    def _fallback_layout(self) -> Dict[str, Tuple[float, float, float]]:
        """Fallback layout when libraries are not available"""
        pos = {}
        nodes = list(self.nodes.keys())
        count = len(nodes)
        
        if count == 0:
            return pos
        
        # Simple circular layout
        for i, node_url in enumerate(nodes):
            angle = 2 * math.pi * i / count
            radius = max(2.0, count * 0.3)
            
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            z = 0.0 if self.mode == "2d" else random.uniform(-1.0, 1.0)
            
            pos[node_url] = (x, y, z)
        
        return pos

class VisualizationRenderer(QWidget):
    """Renders the site visualization"""
    
    node_selected = pyqtSignal(str)  # node_url
    node_hovered = pyqtSignal(str)   # node_url
    
    def __init__(self, layout_engine: NetworkLayoutEngine):
        super().__init__()
        self.layout_engine = layout_engine
        self.selected_node = None
        self.hovered_node = None
        self.zoom_level = 1.0
        self.pan_offset = QPoint(0, 0)
        self.show_labels = True
        self.color_scheme = "status"  # status, depth, domain, response_time
        
        self.setMinimumSize(800, 600)
        self.setMouseTracking(True)
    
    def paintEvent(self, a0):
        """Paint the visualization"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Clear background
        painter.fillRect(self.rect(), QColor(20, 20, 20))
        
        # Apply transformations
        painter.translate(self.width() / 2 + self.pan_offset.x(), 
                         self.height() / 2 + self.pan_offset.y())
        painter.scale(self.zoom_level, self.zoom_level)
        
        # Draw links first (behind nodes)
        self._draw_links(painter)
        
        # Draw nodes
        self._draw_nodes(painter)
        
        # Draw labels if enabled
        if self.show_labels:
            self._draw_labels(painter)
    
    def _draw_links(self, painter: QPainter):
        """Draw links between nodes"""
        for link in self.layout_engine.links:
            source_node = self.layout_engine.nodes.get(link.source_url)
            target_node = self.layout_engine.nodes.get(link.target_url)
            
            if not source_node or not target_node:
                continue
            
            # Get positions (scale for screen coordinates)
            sx, sy = source_node.coordinates[0] * 100, source_node.coordinates[1] * 100
            tx, ty = target_node.coordinates[0] * 100, target_node.coordinates[1] * 100
            
            # Set pen based on link type
            pen = QPen(self._get_link_color(link), 2)
            if link.link_type == "redirect":
                pen.setStyle(Qt.PenStyle.DashLine)
            elif link.link_type == "form":
                pen.setColor(QColor(255, 165, 0))  # Orange
            
            painter.setPen(pen)
            painter.drawLine(int(sx), int(sy), int(tx), int(ty))
            
            # Draw arrow head
            self._draw_arrow_head(painter, sx, sy, tx, ty)
    
    def _draw_nodes(self, painter: QPainter):
        """Draw nodes"""
        for node_url, node in self.layout_engine.nodes.items():
            x, y = node.coordinates[0] * 100, node.coordinates[1] * 100
            
            # Node size based on data extracted
            base_size = 8
            size = base_size + min(node.data_extracted * 2, 20)
            
            # Node color based on color scheme
            color = self._get_node_color(node)
            
            # Special highlighting
            if node_url == self.selected_node:
                painter.setPen(QPen(QColor(255, 255, 255), 3))
            elif node_url == self.hovered_node:
                painter.setPen(QPen(QColor(200, 200, 200), 2))
            else:
                painter.setPen(QPen(QColor(100, 100, 100), 1))
            
            painter.setBrush(QBrush(color))
            
            # Draw node shape based on type
            if node.node_type == "domain":
                # Diamond for domains
                points = [
                    QPoint(int(x), int(y - size)),
                    QPoint(int(x + size), int(y)),
                    QPoint(int(x), int(y + size)),
                    QPoint(int(x - size), int(y))
                ]
                painter.drawPolygon(points)
            elif node.node_type == "external":
                # Square for external links
                painter.drawRect(int(x - size/2), int(y - size/2), size, size)
            else:
                # Circle for regular pages
                painter.drawEllipse(int(x - size/2), int(y - size/2), size, size)
    
    def _draw_labels(self, painter: QPainter):
        """Draw node labels"""
        font = QFont("Arial", 8)
        painter.setFont(font)
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        
        for node_url, node in self.layout_engine.nodes.items():
            x, y = node.coordinates[0] * 100, node.coordinates[1] * 100
            
            # Show title or domain name
            label = node.title if node.title else node.domain
            if len(label) > 20:
                label = label[:17] + "..."
            
            # Offset label below node
            painter.drawText(int(x - 40), int(y + 20), label)
    
    def _draw_arrow_head(self, painter: QPainter, sx: float, sy: float, tx: float, ty: float):
        """Draw arrow head on links"""
        # Calculate arrow direction
        dx = tx - sx
        dy = ty - sy
        length = math.sqrt(dx*dx + dy*dy)
        
        if length == 0:
            return
        
        # Normalize
        dx /= length
        dy /= length
        
        # Arrow head size
        head_size = 8
        
        # Calculate arrow head points
        head_x = tx - dx * head_size
        head_y = ty - dy * head_size
        
        # Perpendicular vector
        px = -dy * head_size * 0.5
        py = dx * head_size * 0.5
        
        # Draw arrow head
        points = [
            QPoint(int(tx), int(ty)),
            QPoint(int(head_x + px), int(head_y + py)),
            QPoint(int(head_x - px), int(head_y - py))
        ]
        painter.drawPolygon(points)
    
    def _get_node_color(self, node: SiteNode) -> QColor:
        """Get node color based on color scheme"""
        if self.color_scheme == "status":
            if node.status_code == 200:
                return QColor(0, 255, 0)  # Green for success
            elif node.status_code >= 400:
                return QColor(255, 0, 0)  # Red for errors
            elif node.status_code >= 300:
                return QColor(255, 255, 0)  # Yellow for redirects
            else:
                return QColor(128, 128, 128)  # Gray for others
                
        elif self.color_scheme == "depth":
            # Color gradient based on crawl depth
            max_depth = max([n.crawl_depth for n in self.layout_engine.nodes.values()], default=1)
            ratio = node.crawl_depth / max_depth
            return QColor(int(255 * ratio), int(255 * (1 - ratio)), 128)
            
        elif self.color_scheme == "domain":
            # Hash domain name to color
            hash_value = hash(node.domain) % 360
            return QColor.fromHsv(hash_value, 200, 255)
            
        elif self.color_scheme == "response_time":
            # Color based on response time (red = slow, green = fast)
            if node.response_time > 2.0:
                return QColor(255, 0, 0)  # Red for slow
            elif node.response_time > 1.0:
                return QColor(255, 165, 0)  # Orange for medium
            else:
                return QColor(0, 255, 0)  # Green for fast
        
        return QColor(128, 128, 255)  # Default blue
    
    def _get_link_color(self, link: SiteLink) -> QColor:
        """Get link color based on type"""
        colors = {
            "hyperlink": QColor(100, 100, 100),
            "redirect": QColor(255, 255, 0),
            "form": QColor(255, 165, 0),
            "ajax": QColor(0, 255, 255)
        }
        return colors.get(link.link_type, QColor(128, 128, 128))
    
    def mousePressEvent(self, a0):
        """Handle mouse press events"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if clicked on a node
            clicked_node = self._get_node_at_position(event.pos())
            if clicked_node:
                self.selected_node = clicked_node
                self.node_selected.emit(clicked_node)
                self.update()
    
    def mouseMoveEvent(self, a0):
        """Handle mouse move events"""
        # Check if hovering over a node
        hovered_node = self._get_node_at_position(event.pos())
        if hovered_node != self.hovered_node:
            self.hovered_node = hovered_node
            if hovered_node:
                self.node_hovered.emit(hovered_node)
            self.update()
    
    def wheelEvent(self, a0):
        """Handle zoom with mouse wheel"""
        delta = event.angleDelta().y()
        zoom_factor = 1.1 if delta > 0 else 0.9
        self.zoom_level = max(0.1, min(5.0, self.zoom_level * zoom_factor))
        self.update()
    
    def _get_node_at_position(self, pos: QPoint) -> Optional[str]:
        """Get node at screen position"""
        # Convert screen coordinates to visualization coordinates
        center_x = self.width() / 2 + self.pan_offset.x()
        center_y = self.height() / 2 + self.pan_offset.y()
        
        x = (pos.x() - center_x) / self.zoom_level
        y = (pos.y() - center_y) / self.zoom_level
        
        # Check each node
        for node_url, node in self.layout_engine.nodes.items():
            node_x = node.coordinates[0] * 100
            node_y = node.coordinates[1] * 100
            
            # Calculate distance
            distance = math.sqrt((x - node_x)**2 + (y - node_y)**2)
            
            # Node size
            base_size = 8
            size = base_size + min(node.data_extracted * 2, 20)
            
            if distance <= size:
                return node_url
        
        return None

class SiteVisualizationWidget(QWidget):
    """Main site visualization widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout_engine = NetworkLayoutEngine(mode="2d")
        self.renderer = VisualizationRenderer(self.layout_engine)
        self.crawl_data: Dict[str, Any] = {}
        
        self.setup_ui()
        self.connect_signals()
        
        # Load sample data for demonstration
        self.load_sample_data()
    
    def setup_ui(self):
        """Setup the visualization UI"""
        layout = QVBoxLayout(self)
        
        # Control panel
        controls_group = QGroupBox("Visualization Controls")
        controls_layout = QGridLayout(controls_group)
        
        # Layout algorithm selector
        controls_layout.addWidget(QLabel("Layout:"), 0, 0)
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(["spring", "circular", "hierarchical", "force_directed"])
        controls_layout.addWidget(self.layout_combo, 0, 1)
        
        # Color scheme selector
        controls_layout.addWidget(QLabel("Colors:"), 0, 2)
        self.color_combo = QComboBox()
        self.color_combo.addItems(["status", "depth", "domain", "response_time"])
        controls_layout.addWidget(self.color_combo, 0, 3)
        
        # 2D/3D toggle
        self.mode_2d = QCheckBox("2D Mode")
        self.mode_2d.setChecked(True)
        controls_layout.addWidget(self.mode_2d, 1, 0)
        
        # Show labels toggle
        self.show_labels = QCheckBox("Show Labels")
        self.show_labels.setChecked(True)
        controls_layout.addWidget(self.show_labels, 1, 1)
        
        # Refresh button
        self.refresh_btn = QPushButton("Refresh Layout")
        controls_layout.addWidget(self.refresh_btn, 1, 2)
        
        # Export button
        self.export_btn = QPushButton("Export Image")
        controls_layout.addWidget(self.export_btn, 1, 3)
        
        # Create splitter for main content
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Visualization area
        viz_widget = QWidget()
        viz_layout = QVBoxLayout(viz_widget)
        viz_layout.addWidget(self.renderer)
        splitter.addWidget(viz_widget)
        
        # Info panel
        info_panel = self.create_info_panel()
        splitter.addWidget(info_panel)
        
        # Set splitter sizes
        splitter.setSizes([600, 200])
        
        layout.addWidget(controls_group)
        layout.addWidget(splitter)
    
    def create_info_panel(self) -> QWidget:
        """Create information panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Node information
        node_group = QGroupBox("Node Information")
        node_layout = QVBoxLayout(node_group)
        
        self.node_info = QTextEdit()
        self.node_info.setMaximumHeight(150)
        self.node_info.setReadOnly(True)
        node_layout.addWidget(self.node_info)
        
        # Statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_text = QTextEdit()
        self.stats_text.setMaximumHeight(100)
        self.stats_text.setReadOnly(True)
        stats_layout.addWidget(self.stats_text)
        
        # Node list
        nodes_group = QGroupBox("Nodes")
        nodes_layout = QVBoxLayout(nodes_group)
        
        self.nodes_list = QListWidget()
        nodes_layout.addWidget(self.nodes_list)
        
        layout.addWidget(node_group)
        layout.addWidget(stats_group)
        layout.addWidget(nodes_group)
        
        return panel
    
    def connect_signals(self):
        """Connect UI signals"""
        self.layout_combo.currentTextChanged.connect(self.update_layout)
        self.color_combo.currentTextChanged.connect(self.update_colors)
        self.mode_2d.stateChanged.connect(self.toggle_mode)
        self.show_labels.stateChanged.connect(self.toggle_labels)
        self.refresh_btn.clicked.connect(self.refresh_visualization)
        self.export_btn.clicked.connect(self.export_visualization)
        
        self.renderer.node_selected.connect(self.on_node_selected)
        self.renderer.node_hovered.connect(self.on_node_hovered)
        
        self.nodes_list.itemClicked.connect(self.on_node_list_clicked)
    
    def load_sample_data(self):
        """Load sample crawl data for demonstration"""
        # Create sample nodes
        domains = ["example.com", "test.org", "demo.net"]
        pages = ["/", "/about", "/contact", "/products", "/blog", "/admin"]
        
        for i, domain in enumerate(domains):
            for j, page in enumerate(pages):
                url = f"https://{domain}{page}"
                
                node = SiteNode(
                    url=url,
                    domain=domain,
                    title=f"{domain.title()} - {page[1:].title() or 'Home'}",
                    status_code=random.choice([200, 200, 200, 404, 301]),
                    response_time=random.uniform(0.1, 3.0),
                    crawl_depth=j,
                    links_found=random.randint(0, 20),
                    data_extracted=random.randint(0, 50),
                    last_crawled=datetime.now(),
                    node_type="page" if page != "/" else "domain"
                )
                
                self.layout_engine.add_node(node)
        
        # Create sample links
        nodes = list(self.layout_engine.nodes.keys())
        for i in range(len(nodes)):
            for j in range(min(3, len(nodes))):  # Each node links to up to 3 others
                if i != j:
                    source = nodes[i]
                    target = nodes[(i + j + 1) % len(nodes)]
                    
                    link = SiteLink(
                        source_url=source,
                        target_url=target,
                        link_type=random.choice(["hyperlink", "redirect", "form"]),
                        weight=random.uniform(0.1, 1.0),
                        discovered_at=datetime.now()
                    )
                    
                    self.layout_engine.add_link(link)
        
        self.refresh_visualization()
    
    def update_layout(self):
        """Update visualization layout"""
        algorithm = self.layout_combo.currentText()
        self.layout_engine.calculate_layout(algorithm)
        self.renderer.update()
    
    def update_colors(self):
        """Update color scheme"""
        scheme = self.color_combo.currentText()
        self.renderer.color_scheme = scheme
        self.renderer.update()
    
    def toggle_mode(self, state):
        """Toggle between 2D and 3D mode"""
        mode = "2d" if state == Qt.CheckState.Checked.value else "3d"
        self.layout_engine.mode = mode
        self.refresh_visualization()
    
    def toggle_labels(self, state):
        """Toggle label visibility"""
        self.renderer.show_labels = state == Qt.CheckState.Checked.value
        self.renderer.update()
    
    def refresh_visualization(self):
        """Refresh the entire visualization"""
        algorithm = self.layout_combo.currentText()
        self.layout_engine.calculate_layout(algorithm)
        self.update_node_list()
        self.update_statistics()
        self.renderer.update()
    
    def update_node_list(self):
        """Update the node list"""
        self.nodes_list.clear()
        
        for node_url, node in self.layout_engine.nodes.items():
            item_text = f"{node.domain} - {node.title[:30]}"
            if node.status_code != 200:
                item_text += f" ({node.status_code})"
            
            self.nodes_list.addItem(item_text)
    
    def update_statistics(self):
        """Update statistics display"""
        nodes = self.layout_engine.nodes
        links = self.layout_engine.links
        
        total_nodes = len(nodes)
        total_links = len(links)
        domains = len(set(node.domain for node in nodes.values()))
        
        avg_response_time = sum(node.response_time for node in nodes.values()) / total_nodes if total_nodes > 0 else 0
        success_rate = sum(1 for node in nodes.values() if node.status_code == 200) / total_nodes * 100 if total_nodes > 0 else 0
        
        stats_text = f"""
Total Nodes: {total_nodes}
Total Links: {total_links}
Unique Domains: {domains}
Avg Response Time: {avg_response_time:.2f}s
Success Rate: {success_rate:.1f}%
        """.strip()
        
        self.stats_text.setText(stats_text)
    
    def on_node_selected(self, node_url: str):
        """Handle node selection"""
        node = self.layout_engine.nodes.get(node_url)
        if not node:
            return
        
        info_text = f"""
URL: {node.url}
Domain: {node.domain}
Title: {node.title}
Status: {node.status_code}
Response Time: {node.response_time:.2f}s
Crawl Depth: {node.crawl_depth}
Links Found: {node.links_found}
Data Extracted: {node.data_extracted}
Last Crawled: {node.last_crawled}
Node Type: {node.node_type}
        """.strip()
        
        self.node_info.setText(info_text)
    
    def on_node_hovered(self, node_url: str):
        """Handle node hover"""
        # Could show tooltip or status bar info
        pass
    
    def on_node_list_clicked(self, item):
        """Handle node list item click"""
        # Find corresponding node and select it
        item_index = self.nodes_list.row(item)
        if item_index < len(self.layout_engine.nodes):
            node_url = list(self.layout_engine.nodes.keys())[item_index]
            self.renderer.selected_node = node_url
            self.on_node_selected(node_url)
            self.renderer.update()
    
    def export_visualization(self):
        """Export visualization as image"""
        try:
            pixmap = self.renderer.grab()
            filename = f"site_visualization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            success = pixmap.save(filename)
            
            if success:
                logger.info(f"Visualization exported to {filename}")
            else:
                logger.error("Failed to export visualization")
                
        except Exception as e:
            logger.error(f"Error exporting visualization: {e}")
    
    def load_crawl_data(self, data: Dict[str, Any]):
        """Load crawl data into visualization"""
        self.crawl_data = data
        
        # Clear existing data
        self.layout_engine.nodes.clear()
        self.layout_engine.links.clear()
        
        # Process crawl data
        if 'sites' in data:
            for site_data in data['sites']:
                node = SiteNode(
                    url=site_data.get('url', ''),
                    domain=site_data.get('domain', ''),
                    title=site_data.get('title', ''),
                    status_code=site_data.get('status_code', 200),
                    response_time=site_data.get('response_time', 0.0),
                    crawl_depth=site_data.get('crawl_depth', 0),
                    links_found=site_data.get('links_found', 0),
                    data_extracted=site_data.get('data_extracted', 0),
                    node_type=site_data.get('node_type', 'page')
                )
                self.layout_engine.add_node(node)
        
        if 'links' in data:
            for link_data in data['links']:
                link = SiteLink(
                    source_url=link_data.get('source_url', ''),
                    target_url=link_data.get('target_url', ''),
                    link_type=link_data.get('link_type', 'hyperlink'),
                    weight=link_data.get('weight', 1.0)
                )
                self.layout_engine.add_link(link)
        
        self.refresh_visualization()
    
    def get_visualization_data(self) -> Dict[str, Any]:
        """Get current visualization data"""
        return {
            'nodes': {
                url: {
                    'domain': node.domain,
                    'title': node.title,
                    'status_code': node.status_code,
                    'response_time': node.response_time,
                    'crawl_depth': node.crawl_depth,
                    'links_found': node.links_found,
                    'data_extracted': node.data_extracted,
                    'coordinates': node.coordinates,
                    'node_type': node.node_type
                }
                for url, node in self.layout_engine.nodes.items()
            },
            'links': [
                {
                    'source_url': link.source_url,
                    'target_url': link.target_url,
                    'link_type': link.link_type,
                    'weight': link.weight
                }
                for link in self.layout_engine.links
            ],
            'statistics': {
                'total_nodes': len(self.layout_engine.nodes),
                'total_links': len(self.layout_engine.links),
                'unique_domains': len(set(node.domain for node in self.layout_engine.nodes.values()))
            }
        }
