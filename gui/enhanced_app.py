"""
Main Application Integration with Enhanced Tooltip System
"""
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMainWindow
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QIcon
except ImportError:
    from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMainWindow
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QIcon

from gui.components.tooltip_system import tooltip_manager, ExperienceLevelSelector, TooltipWidget
from gui.components.dashboard import DashboardWindow
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedMainWindow(QMainWindow):
    """Enhanced main window with integrated tooltip system"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Business Intelligence Scraper - Enhanced")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        
        # Top toolbar with experience level selector
        toolbar_layout = QHBoxLayout()
        
        # Experience level selector
        self.experience_selector = ExperienceLevelSelector()
        toolbar_layout.addWidget(QLabel("User Experience:"))
        toolbar_layout.addWidget(self.experience_selector)
        
        # Add some example tooltip buttons
        self.create_demo_buttons(toolbar_layout)
        
        toolbar_layout.addStretch()
        
        # Add the dashboard
        self.dashboard = DashboardWindow()
        
        layout.addLayout(toolbar_layout)
        layout.addWidget(self.dashboard)
        
        # Connect experience level changes
        self.experience_selector.level_changed.connect(self.on_experience_level_changed)
        
        # Initialize with beginner level
        tooltip_manager.set_experience_level("beginner")
        
    def create_demo_buttons(self, layout):
        """Create demo buttons to showcase tooltip functionality"""
        
        # Spider configuration button
        self.spider_btn = TooltipDemoButton("Spider Config", "spider_config")
        layout.addWidget(self.spider_btn)
        
        # Proxy rotation button  
        self.proxy_btn = TooltipDemoButton("Proxy Setup", "proxy_rotation")
        layout.addWidget(self.proxy_btn)
        
        # Performance metrics button
        self.metrics_btn = TooltipDemoButton("Performance", "performance_metrics")
        layout.addWidget(self.metrics_btn)
        
    def on_experience_level_changed(self, level: str):
        """Handle experience level changes"""
        logger.info(f"Experience level changed to: {level}")
        # The tooltip manager is automatically updated via the signal

class TooltipDemoButton(TooltipWidget):
    """Demo button with tooltip functionality"""
    
    def __init__(self, text: str, tooltip_id: str):
        super().__init__(tooltip_id=tooltip_id)
        
        self.button = QPushButton(text)
        self.button.setMinimumHeight(35)
        
        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.button)
        layout.setContentsMargins(2, 2, 2, 2)
        
        # Connect button click
        self.button.clicked.connect(self.on_button_clicked)
        
    def on_button_clicked(self):
        """Handle button click"""
        logger.info(f"Button clicked: {self.tooltip_id}")

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Business Intelligence Scraper")
    app.setOrganizationName("BI Scraper")
    
    # Set application icon if available
    icon_path = Path("gui/assets/icon.png")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # Create and show main window
    window = EnhancedMainWindow()
    window.show()
    
    logger.info("Application started with enhanced tooltip system")
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
