"""GUI launcher entry point for the Business Intelligence Scraper."""

from __future__ import annotations

import sys
from pathlib import Path

# PyQt6 is preferred. Fallback to PyQt5 if needed.
try:
    from PyQt6 import QtWidgets
except ImportError:  # pragma: no cover - optional dependency
    from PyQt5 import QtWidgets  # type: ignore

from .components.dashboard import DashboardWindow


BASE_DIR = Path(__file__).resolve().parent


def main() -> None:
    """Launch the main GUI application."""

    app = QtWidgets.QApplication(sys.argv)
    window = DashboardWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
