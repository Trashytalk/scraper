"""Main dashboard window for the GUI."""

from __future__ import annotations

from pathlib import Path
from typing import Any

# PyQt6 is preferred. Fallback to PyQt5 if needed.
try:
    from PyQt6 import QtWidgets
except ImportError:  # pragma: no cover - optional dependency
    from PyQt5 import QtWidgets  # type: ignore

from .job_manager import JobManagerWidget
from .log_viewer import LogViewerWidget
from .data_viewer import DataViewerWidget
from .config_dialog import ConfigDialog


class DashboardWindow(QtWidgets.QMainWindow):
    """Main window aggregating all components."""

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Business Intelligence Scraper")
        self.resize(1024, 768)

        # Central widgets
        self.job_manager = JobManagerWidget()
        self.log_viewer = LogViewerWidget()
        self.data_viewer = DataViewerWidget()

        self.tabs = QtWidgets.QTabWidget()
        self.tabs.addTab(self.job_manager, "Jobs")
        self.tabs.addTab(self.log_viewer, "Logs")
        self.tabs.addTab(self.data_viewer, "Data")

        self.setCentralWidget(self.tabs)
        self._create_menu()

    def _create_menu(self) -> None:
        """Create basic menu actions."""

        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        config_action = file_menu.addAction("Configuration")
        config_action.triggered.connect(self.show_config_dialog)
        quit_action = file_menu.addAction("Quit")
        quit_action.triggered.connect(self.close)

    def show_config_dialog(self) -> None:
        """Display the configuration dialog."""

        dialog = ConfigDialog(self)
        dialog.exec()

    def closeEvent(self, event: Any) -> None:  # noqa: D401 - Qt override
        """Handle window close event and perform cleanup."""

        # TODO: gracefully stop running jobs if any
        super().closeEvent(event)
