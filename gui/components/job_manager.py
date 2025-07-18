"""Widget for launching and monitoring scraping jobs."""

from __future__ import annotations

import threading
from typing import Any, Callable

# PyQt6 is preferred. Fallback to PyQt5 if needed.
try:
    from PyQt6 import QtCore, QtWidgets
except ImportError:  # pragma: no cover - optional dependency
    from PyQt5 import QtCore, QtWidgets  # type: ignore

# TODO: import the actual scraping functions from the scraper package
# from business_intel_scraper.backend.workers.tasks import launch_scraping_task


class JobManagerWidget(QtWidgets.QWidget):
    """Manage spider jobs and show their status."""

    job_started = QtCore.pyqtSignal(str)  # type: ignore[attr-defined]
    job_finished = QtCore.pyqtSignal(str)  # type: ignore[attr-defined]

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        """
        Initialize the JobManagerWidget, set up the user interface, and prepare internal job tracking.
        
        Parameters:
            parent (QtWidgets.QWidget | None): Optional parent widget.
        """
        super().__init__(parent)
        self._setup_ui()
        self.active_jobs: dict[str, str] = {}

    def _setup_ui(self) -> None:
        """
        Set up the user interface for the job manager widget, including input fields, control buttons, and a log display.
        """
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
        """
        Starts a new simulated scraping job in a background thread and updates job status.
        
        The method retrieves the spider name from the input field (defaulting to "example" if empty), creates a unique job ID, marks the job as running, emits job status signals, and logs job events. The job simulation runs asynchronously to avoid blocking the UI.
        """

        spider = self.spider_name.text().strip() or "example"

        def _run() -> None:
            # TODO: connect to scraper task runner instead of dummy logic
            """
            Simulates the execution of a scraping job, updating job status, emitting job signals, and logging progress.
            
            This function generates a unique job ID, marks the job as running, emits a job started signal, logs the start, waits for a fixed duration to simulate work, then marks the job as finished, emits a job finished signal, and logs the completion.
            """
            job_id = f"job-{len(self.active_jobs)+1}"
            self.active_jobs[job_id] = "running"
            self.job_started.emit(job_id)
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
        """
        Logs a request to stop all running jobs. Actual job cancellation is not implemented.
        """

        # TODO: implement proper job cancellation via scraper APIs
        self._append_log("Requested stop for all jobs (not yet implemented)")

    def _append_log(self, message: str) -> None:
        """
        Appends a message to the log display in the widget.
        """
        self.log.append(message)
