"""Widget for viewing scraped data."""

from __future__ import annotations

# PyQt6 is preferred. Fallback to PyQt5 if needed.
try:
    from PyQt6 import QtWidgets
except ImportError:  # pragma: no cover - optional dependency
    from PyQt5 import QtWidgets  # type: ignore


class DataViewerWidget(QtWidgets.QTableWidget):
    """Display scraped data in a table view."""

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        """
        Initialize the DataViewerWidget with zero rows and columns.
        
        Parameters:
        	parent (QWidget, optional): The parent widget, if any.
        """
        super().__init__(parent)
        self.setColumnCount(0)
        self.setRowCount(0)
        # TODO: load scraped data from the scraper package

    def load_data(self, items: list[dict[str, str]]) -> None:
        """
        Populate the table with rows from a list of dictionaries.
        
        Each dictionary in the list represents a row, with keys as column headers and values as cell contents. Existing table content is cleared before loading new data. If the list is empty, the table remains empty.
        """

        self.clear()
        if not items:
            return
        headers = list(items[0].keys())
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        self.setRowCount(len(items))
        for row, item in enumerate(items):
            for col, header in enumerate(headers):
                self.setItem(
                    row, col, QtWidgets.QTableWidgetItem(str(item.get(header, "")))
                )
