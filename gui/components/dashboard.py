"""Main dashboard window for the GUI."""

from __future__ import annotations

from pathlib import Path
from typing import Any

# PyQt6 is preferred. Fallback to PyQt5 if needed.
try:
    from PyQt6.QtWidgets import (QMainWindow, QWidget, QApplication, QTabWidget, 
                                QToolBar, QVBoxLayout, QDockWidget)
    from PyQt6.QtCore import Qt
    import PyQt6.QtWidgets as QtWidgets
except ImportError:  # pragma: no cover - optional dependency
    from PyQt5 import QtWidgets  # type: ignore
    from PyQt5.QtCore import Qt  # type: ignore

try:
    from gui.components.job_manager import JobManagerWidget
    from gui.components.log_viewer import LogViewerWidget
    from gui.components.config_dialog import ConfigDialog
    from gui.components.data_viewer import DataViewerWidget
    from gui.components.tooltip_system import TooltipManager
    from gui.components.tor_integration import TORWidget
    from gui.components.network_config import NetworkConfigWidget
    from gui.components.advanced_parsing import ParsingWidget
    from gui.components.embedded_browser import EmbeddedBrowser, BrowserTabWidget, BrowserDockWidget
    from gui.components.data_visualization import SiteVisualizationWidget
    from gui.components.osint_integration import OSINTIntegrationWidget
    from gui.components.data_enrichment import DataEnrichmentWidget
    from gui.components.tooltip_system import tooltip_manager, ExperienceLevelSelector, TooltipWidget
except ImportError:
    # Fallback for relative imports
    from .job_manager import JobManagerWidget
    from .log_viewer import LogViewerWidget
    from .config_dialog import ConfigDialog
    from .data_viewer import DataViewerWidget
    from .tooltip_system import TooltipManager
    from .tor_integration import TORWidget
    from .network_config import NetworkConfigWidget
    from .advanced_parsing import ParsingWidget
    from .embedded_browser import EmbeddedBrowser, BrowserTabWidget, BrowserDockWidget
    from .data_visualization import SiteVisualizationWidget
    from .osint_integration import OSINTIntegrationWidget
    from .data_enrichment import DataEnrichmentWidget
    from .tooltip_system import tooltip_manager, ExperienceLevelSelector, TooltipWidget


class DashboardWindow(QMainWindow):
    """Main window aggregating all components."""

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Business Intelligence Scraper")
        self.resize(1024, 768)

        # Initialize tooltip system
        self.experience_selector = ExperienceLevelSelector()
        
        # Create toolbar with experience level selector
        self.toolbar = QtWidgets.QToolBar("Main Toolbar")
        self.addToolBar(self.toolbar)
        self.toolbar.addWidget(self.experience_selector)
        self.toolbar.addSeparator()

        # Central widgets with tooltip support
        self.job_manager = TooltipJobManagerWidget()
        self.log_viewer = LogViewerWidget()
        self.data_viewer = DataViewerWidget()
        self.tor_widget = TORWidget()  # type: ignore
        self.network_config = NetworkConfigWidget()
        self.parsing_widget = ParsingWidget()  # type: ignore
        self.browser_tabs = BrowserTabWidget()  # type: ignore
        self.visualization_widget = SiteVisualizationWidget()  # type: ignore
        self.osint_widget = OSINTIntegrationWidget()  # type: ignore
        self.enrichment_widget = DataEnrichmentWidget()  # type: ignore

        self.tabs = QtWidgets.QTabWidget()
        self.tabs.addTab(self.job_manager, "Jobs")
        self.tabs.addTab(self.log_viewer, "Logs")
        self.tabs.addTab(self.data_viewer, "Data")
        self.tabs.addTab(self.parsing_widget, "Data Parsing")
        self.tabs.addTab(self.browser_tabs, "Browser")
        self.tabs.addTab(self.network_config, "Network")
        self.tabs.addTab(self.tor_widget, "TOR Network")
        self.tabs.addTab(self.visualization_widget, "Visualization")
        self.tabs.addTab(self.osint_widget, "OSINT")
        self.tabs.addTab(self.enrichment_widget, "Data Enrichment")

        self.setCentralWidget(self.tabs)
        self._create_menu()
        
        # Add dockable browser option
        self.browser_dock = BrowserDockWidget("Browser Panel", self)  # type: ignore
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.browser_dock)
        self.browser_dock.hide()  # Initially hidden

        # Set references in job manager for browser controls
        self.job_manager.browser_dock = self.browser_dock
        self.job_manager.browser_tabs = self.browser_tabs

    def _create_menu(self) -> None:
        """Create basic menu actions."""

        menubar = self.menuBar()
        if menubar is not None:
            file_menu = menubar.addMenu("File")
            if file_menu is not None:
                config_action = file_menu.addAction("Configuration")
                if config_action is not None:
                    config_action.triggered.connect(self.show_config_dialog)
                quit_action = file_menu.addAction("Quit")
                if quit_action is not None:
                    quit_action.triggered.connect(self.close)
            
            # Add browser menu
            browser_menu = menubar.addMenu("Browser")
            if browser_menu is not None:
                toggle_dock_action = browser_menu.addAction("Toggle Browser Panel")
                if toggle_dock_action is not None:
                    toggle_dock_action.triggered.connect(self.toggle_browser_dock)
                new_tab_action = browser_menu.addAction("New Browser Tab")
                if new_tab_action is not None:
                    new_tab_action.triggered.connect(self.add_browser_tab)
        
    def toggle_browser_dock(self) -> None:
        """Toggle browser dock panel visibility"""
        if self.browser_dock.isVisible():
            self.browser_dock.hide()
        else:
            self.browser_dock.show()
            
    def add_browser_tab(self) -> None:
        """Add new browser tab"""
        self.browser_tabs.add_new_tab()  # type: ignore

    def show_config_dialog(self) -> None:
        """Display the configuration dialog."""

        dialog = ConfigDialog(self)
        dialog.exec()

    def closeEvent(self, a0: Any) -> None:  # noqa: D401 - Qt override
        """Handle window close event and perform cleanup."""

        # TODO: gracefully stop running jobs if any
        super().closeEvent(a0)


class TooltipJobManagerWidget(TooltipWidget):
    """Job manager widget with tooltip support"""
    
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(tooltip_id="job_management", parent=parent)
        self.job_manager = JobManagerWidget(parent=self)
        
        # Layout to contain the original job manager
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.job_manager)
        layout.setContentsMargins(0, 0, 0, 0)

        # Initialize browser dock and tabs references (will be set by parent)
        self.browser_dock: QtWidgets.QDockWidget | None = None
        self.browser_tabs: BrowserTabWidget | None = None
        
    def toggle_browser_dock(self) -> None:
        """Toggle browser dock panel visibility"""
        if self.browser_dock is not None:
            if self.browser_dock.isVisible():
                self.browser_dock.hide()
            else:
                self.browser_dock.show()
            
    def add_browser_tab(self) -> None:
        """Add new browser tab"""
        if self.browser_tabs is not None:
            self.browser_tabs.add_new_tab()  # type: ignore

    def show_config_dialog(self) -> None:
        """Display the configuration dialog."""

        dialog = ConfigDialog(self)
        dialog.exec()

    def closeEvent(self, a0: Any) -> None:  # noqa: D401 - Qt override
        """Handle window close event and perform cleanup."""

        # TODO: gracefully stop running jobs if any
        super().closeEvent(a0)
