"""Dialog for editing scraper configuration."""

from __future__ import annotations

import yaml
from pathlib import Path

# PyQt6 is preferred. Fallback to PyQt5 if needed.
try:
    from PyQt6 import QtWidgets
except ImportError:  # pragma: no cover - optional dependency
    from PyQt5 import QtWidgets  # type: ignore

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "config.yaml"


class ConfigDialog(QtWidgets.QDialog):
    """Simple configuration editor."""

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        """
        Initialize the configuration editor dialog window.
        
        Sets the window title and size, builds the user interface, and loads the current configuration file content into the editor.
        """
        super().__init__(parent)
        self.setWindowTitle("Configuration")
        self.resize(400, 300)
        self._setup_ui()
        self.load_config()

    def _setup_ui(self) -> None:
        """
        Set up the dialog's user interface with a plain text editor and Save/Cancel buttons.
        """
        layout = QtWidgets.QVBoxLayout(self)
        self.text_edit = QtWidgets.QPlainTextEdit()
        layout.addWidget(self.text_edit)
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Save
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.save_config)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def load_config(self) -> None:
        """
        Loads the configuration file content into the text editor.
        
        If the configuration file exists, its contents are displayed in the editor; otherwise, a placeholder comment is shown.
        """

        if CONFIG_PATH.exists():
            self.text_edit.setPlainText(CONFIG_PATH.read_text())
        else:
            self.text_edit.setPlainText("# Configuration file not found\n")

    def save_config(self) -> None:
        """
        Saves the current editor contents to the configuration file and closes the dialog.
        
        Ensures the configuration directory exists before writing.
        """

        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(self.text_edit.toPlainText())
        self.accept()
