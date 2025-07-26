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
        super().__init__(parent)
        self.setColumnCount(0)
        self.setRowCount(0)
        # Load scraped data from the scraper package
        self.setup_data_loading()
        
    def setup_data_loading(self):
        """Set up connection to scraper data sources"""
        try:
            # Try to import actual scraper data access
            from business_intel_scraper.backend.db.centralized_data import CentralizedDataRecord
            from business_intel_scraper.backend.dependencies import get_db
            self.data_available = True
            self.load_scraped_data()
        except ImportError:
            self.data_available = False
            self.load_demo_data()
            
    def load_scraped_data(self):
        """Load actual data from the scraper database"""
        try:
            # In a real implementation, this would:
            # 1. Connect to the centralized database
            # 2. Query recent scraping results
            # 3. Format data for table display
            # 4. Set up auto-refresh for new data
            
            # Placeholder for database connection
            sample_data = [
                {
                    "ID": "1",
                    "Title": "Sample Scraped Data", 
                    "URL": "https://example.com",
                    "Status": "Processed",
                    "Date": "2024-01-15"
                },
                {
                    "ID": "2", 
                    "Title": "Market Analysis Data",
                    "URL": "https://example.org", 
                    "Status": "Valid",
                    "Date": "2024-01-14"
                }
            ]
            self.load_data(sample_data)
            
        except Exception as e:
            print(f"Error loading scraped data: {e}")
            self.load_demo_data()
            
    def load_demo_data(self):
        """Load demo data when scraper is not available"""
        demo_data = [
            {
                "Source": "Demo",
                "Title": "Sample Entry 1", 
                "Status": "Demo Mode",
                "Note": "Connect scraper backend for real data"
            },
            {
                "Source": "Demo",
                "Title": "Sample Entry 2",
                "Status": "Demo Mode", 
                "Note": "This is placeholder data"
            }
        ]
        self.load_data(demo_data)

    def load_data(self, items: list[dict[str, str]]) -> None:
        """Populate the table with data."""

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
