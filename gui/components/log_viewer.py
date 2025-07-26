"""Widget for displaying log output."""

from __future__ import annotations

# PyQt6 is preferred. Fallback to PyQt5 if needed.
try:
    from PyQt6 import QtWidgets, QtCore, QtGui
except ImportError:  # pragma: no cover - optional dependency
    from PyQt5 import QtWidgets, QtCore, QtGui  # type: ignore

import logging


class LogViewerWidget(QtWidgets.QTextEdit):
    """Live-updating log viewer."""

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setReadOnly(True)
        # Stream logs from scraper with real-time updates
        self.setup_log_streaming()
        
    def setup_log_streaming(self):
        """Set up real-time log streaming from the scraper backend"""
        import logging
        import threading
        from queue import Queue
        
        # Create a log queue for thread-safe communication
        self.log_queue = Queue()
        
        # Set up a custom log handler that feeds into our queue
        self.log_handler = QueueLogHandler(self.log_queue)
        self.log_handler.setLevel(logging.INFO)
        self.log_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        
        # Add handler to the scraper loggers
        scraper_loggers = [
            'business_intel_scraper',
            'scraping_engine', 
            'security_alerts',
            'performance_monitor'
        ]
        
        for logger_name in scraper_loggers:
            logger = logging.getLogger(logger_name)
            logger.addHandler(self.log_handler)
        
        # Start the log processing thread
        self.log_thread = threading.Thread(target=self._process_logs, daemon=True)
        self.log_thread.start()
        
    def _process_logs(self):
        """Process logs from the queue and update the widget"""
        while True:
            try:
                # Get log record from queue (blocks until available)
                log_record = self.log_queue.get(timeout=1.0)
                
                # Format and append to the text widget
                formatted_log = self.log_handler.format(log_record)
                
                # Use QTimer to safely update GUI from another thread
                QtCore.QTimer.singleShot(0, lambda: self._append_log_safe(formatted_log))
                
            except:
                # Queue timeout or other error - continue processing
                continue
                
    def _append_log_safe(self, log_text: str):
        """Safely append log text to the widget from any thread"""
        self.append(log_text)
        
        # Auto-scroll to bottom to show latest logs
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        # Limit the number of lines to prevent memory issues
        max_lines = 1000
        document = self.document()
        if document.blockCount() > max_lines:
            cursor = QtGui.QTextCursor(document)
            cursor.movePosition(QtGui.QTextCursor.Start)
            cursor.movePosition(QtGui.QTextCursor.Down, QtGui.QTextCursor.KeepAnchor, 
                              document.blockCount() - max_lines)
            cursor.removeSelectedText()


class QueueLogHandler(logging.Handler):
    """Custom log handler that puts log records into a queue"""
    
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue
        
    def emit(self, record):
        """Add log record to the queue"""
        try:
            self.log_queue.put_nowait(record)
        except:
            # Queue is full or other error - drop the log
            pass
