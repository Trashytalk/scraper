"""Widget for displaying log output."""

from __future__ import annotations

# PyQt6 is preferred. Fallback to PyQt5 if needed.
try:
    from PyQt6 import QtWidgets
except ImportError:  # pragma: no cover - optional dependency
    from PyQt5 import QtWidgets  # type: ignore


class LogViewerWidget(QtWidgets.QTextEdit):
    """Live-updating log viewer."""

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setReadOnly(True)
        # TODO: stream logs from scraper into this widget
