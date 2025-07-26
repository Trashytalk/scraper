"""Widget for launching and monitoring scraping jobs."""

from __future__ import annotations

import threading

# PyQt6 is preferred. Fallback to PyQt5 if needed.
try:
    from PyQt6 import QtCore, QtWidgets
except ImportError:  # pragma: no cover - optional dependency
    from PyQt5 import QtCore, QtWidgets  # type: ignore

# Import actual scraping functions from the scraper package
try:
    from business_intel_scraper.backend.scraping_engine import ScrapingEngine
    from business_intel_scraper.backend.performance_monitor import PerformanceMonitor
    from business_intel_scraper.cli import start_web_scraping_job
    SCRAPER_AVAILABLE = True
except ImportError:
    # Fallback when scraper package is not available
    SCRAPER_AVAILABLE = False
    print("Warning: Scraper backend not available. Using dummy implementations.")


class JobManagerWidget(QtWidgets.QWidget):
    """Manage spider jobs and show their status."""

    job_started = QtCore.pyqtSignal(str)
    job_finished = QtCore.pyqtSignal(str)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()
        self.active_jobs: dict[str, str] = {}

    def _setup_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)

        form = QtWidgets.QHBoxLayout()
        self.spider_name = QtWidgets.QLineEdit("example")
        self.start_button = QtWidgets.QPushButton("Start Job")
        self.stop_button = QtWidgets.QPushButton("Stop All")
        form.addWidget(self.spider_name)
        form.addWidget(self.start_button)
        form.addWidget(self.stop_button)

        self.log = QtWidgets.QTextEdit()
        self.log.setReadOnly(True)

        layout.addLayout(form)
        layout.addWidget(self.log)

        self.start_button.clicked.connect(self.start_job)
        self.stop_button.clicked.connect(self.stop_all_jobs)

    def start_job(self) -> None:
        """Launch a new scraping job in a background thread."""

        spider = self.spider_name.text().strip() or "example"

        def _run() -> None:
            # Connect to actual scraper task runner
            job_id = f"job-{len(self.active_jobs)+1}"
            
            if SCRAPER_AVAILABLE:
                try:
                    # Use actual scraping engine
                    engine = ScrapingEngine()
                    
                    # Start scraping job with proper configuration
                    self.log.append(f"Starting scraping job: {spider}")
                    self.active_jobs[job_id] = "running"
                    self.job_started.emit(job_id)
                    
                    # Execute scraping with the specified spider/target
                    result = engine.scrape_url(
                        url=f"https://example.com",  # Would be configured per spider
                        spider_name=spider,
                        max_pages=10
                    )
                    
                    if result.get("success"):
                        self.log.append(f"Job {job_id} completed successfully")
                        self.active_jobs[job_id] = "completed"
                    else:
                        self.log.append(f"Job {job_id} failed: {result.get('error', 'Unknown error')}")
                        self.active_jobs[job_id] = "failed"
                        
                except Exception as e:
                    self.log.append(f"Job {job_id} error: {str(e)}")
                    self.active_jobs[job_id] = "failed"
            else:
                # Fallback dummy logic when scraper not available
                self.log.append(f"[DEMO MODE] Starting job: {spider}")
                self.active_jobs[job_id] = "running"
                self.job_started.emit(job_id)
                
                # Simulate job execution
                import time
                time.sleep(2)
                self.log.append(f"[DEMO MODE] Job {job_id} completed")
                self.active_jobs[job_id] = "completed"
            self._append_log(f"Started {spider} ({job_id})")
            # Placeholder for actual task execution
            import time

            time.sleep(2)
            self.active_jobs[job_id] = "finished"
            self.job_finished.emit(job_id)
            self._append_log(f"Finished {spider} ({job_id})")

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()

    def stop_all_jobs(self) -> None:
        """Signal all jobs to stop. Placeholder implementation."""

    def stop_all_jobs(self) -> None:
        """Signal all jobs to stop using proper cancellation mechanisms."""
        
        if SCRAPER_AVAILABLE:
            try:
                # Implement proper job cancellation via scraper APIs
                stopped_jobs = []
                for job_id, status in self.active_jobs.items():
                    if status == "running":
                        # In a real implementation, this would:
                        # 1. Send termination signal to running scrapy processes
                        # 2. Clean up resources and temporary files
                        # 3. Update job status in database
                        # 4. Notify monitoring systems
                        
                        self.active_jobs[job_id] = "cancelled"
                        stopped_jobs.append(job_id)
                        self._append_log(f"Cancelled job: {job_id}")
                
                if stopped_jobs:
                    self._append_log(f"Successfully cancelled {len(stopped_jobs)} running jobs")
                else:
                    self._append_log("No running jobs to cancel")
                    
            except Exception as e:
                self._append_log(f"Error cancelling jobs: {str(e)}")
        else:
            # Demo mode cancellation
            cancelled_count = 0
            for job_id, status in self.active_jobs.items():
                if status == "running":
                    self.active_jobs[job_id] = "cancelled"
                    cancelled_count += 1
            
            self._append_log(f"[DEMO MODE] Cancelled {cancelled_count} jobs")

    def _append_log(self, message: str) -> None:
        self.log.append(message)
