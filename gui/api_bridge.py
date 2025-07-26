"""API bridge for communicating with a PyWebview frontend."""

from __future__ import annotations

# This module is optional and can be used to expose Python functions
# to a JavaScript frontend when using PyWebview.

from typing import Any, Dict, List, Optional
import logging
import asyncio
import json
from datetime import datetime


class ApiBridge:
    """Expose scraper functionality to a web frontend."""

    def __init__(self) -> None:
        # Initialize references to scraper modules
        self.jobs = {}  # In-memory job storage
        self.job_counter = 0
        self.logs = []  # In-memory log storage
        self._setup_logging()
        
        # Try to import scraper engine
        try:
            import sys
            import os
            # Add parent directory to path to access scraper modules
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if parent_dir not in sys.path:
                sys.path.append(parent_dir)
            
            from scraping_engine import ScrapingEngine
            self.scraper = ScrapingEngine()
            self.scraper_available = True
        except ImportError as e:
            logging.warning(f"Scraper engine not available: {e}")
            self.scraper = None
            self.scraper_available = False

    def _setup_logging(self) -> None:
        """Setup logging to capture logs for GUI display."""
        # Create a custom log handler that stores logs in memory
        class GuiLogHandler(logging.Handler):
            def __init__(self, api_bridge):
                super().__init__()
                self.api_bridge = api_bridge
                
            def emit(self, record):
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "level": record.levelname,
                    "message": self.format(record),
                    "module": record.module
                }
                self.api_bridge.logs.append(log_entry)
                # Keep only last 1000 log entries
                if len(self.api_bridge.logs) > 1000:
                    self.api_bridge.logs = self.api_bridge.logs[-1000:]
        
        # Add our handler to the root logger
        handler = GuiLogHandler(self)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logging.getLogger().addHandler(handler)

    def launch_job(self, spider: str, url: str = "", config: Optional[Dict[str, Any]] = None) -> str:
        """Launch a spider and return a job id."""
        self.job_counter += 1
        job_id = f"job-{self.job_counter}"
        
        if config is None:
            config = {}
        
        job_data = {
            "id": job_id,
            "spider": spider,
            "url": url,
            "config": config,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
            "results": [],
            "error": None
        }
        
        self.jobs[job_id] = job_data
        
        if self.scraper_available and url:
            # Launch actual scraping job asynchronously
            self._start_scraping_job(job_id, url, config)
        else:
            # Simulate job completion for demo purposes
            import threading
            import time
            
            def simulate_job():
                time.sleep(2)  # Simulate processing time
                self.jobs[job_id]["status"] = "completed"
                self.jobs[job_id]["completed_at"] = datetime.now().isoformat()
                self.jobs[job_id]["results"] = [
                    {
                        "title": f"Sample Result from {spider}",
                        "url": url or "https://example.com",
                        "text": "This is simulated scraped content.",
                        "timestamp": datetime.now().isoformat()
                    }
                ]
                logging.info(f"Job {job_id} completed successfully")
            
            threading.Thread(target=simulate_job, daemon=True).start()
            
        self.jobs[job_id]["status"] = "running"
        self.jobs[job_id]["started_at"] = datetime.now().isoformat()
        
        logging.info(f"Launched job {job_id} with spider {spider}")
        return job_id

    def _start_scraping_job(self, job_id: str, url: str, config: Dict[str, Any]) -> None:
        """Start actual scraping job in background."""
        import threading
        
        def run_scraper():
            loop = None
            try:
                if not self.scraper:
                    raise RuntimeError("Scraper not available")
                    
                # Run the scraper
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Use the scrape_url method with config
                result = loop.run_until_complete(
                    self.scraper.scrape_url(url, "basic", config)
                )
                
                # Update job with results
                self.jobs[job_id]["status"] = "completed"
                self.jobs[job_id]["completed_at"] = datetime.now().isoformat()
                self.jobs[job_id]["results"] = [result] if result else []
                
                logging.info(f"Job {job_id} completed successfully")
                
            except Exception as e:
                self.jobs[job_id]["status"] = "failed"
                self.jobs[job_id]["completed_at"] = datetime.now().isoformat()
                self.jobs[job_id]["error"] = str(e)
                logging.error(f"Job {job_id} failed: {e}")
            finally:
                if loop:
                    loop.close()
        
        threading.Thread(target=run_scraper, daemon=True).start()

    def get_job_status(self, job_id: str) -> str:
        """Return status for a given job."""
        if job_id in self.jobs:
            return self.jobs[job_id]["status"]
        return "not_found"

    def get_job_details(self, job_id: str) -> Dict[str, Any]:
        """Return detailed information about a job."""
        if job_id in self.jobs:
            return self.jobs[job_id]
        return {"error": "Job not found"}

    def list_jobs(self) -> List[Dict[str, Any]]:
        """Return list of all jobs."""
        return list(self.jobs.values())

    def get_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Return recent log lines."""
        return self.logs[-limit:] if limit else self.logs

    def get_data(self, job_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return scraped data."""
        if job_id:
            # Return data for specific job
            if job_id in self.jobs:
                return self.jobs[job_id].get("results", [])
            return []
        else:
            # Return all scraped data
            all_data = []
            for job in self.jobs.values():
                all_data.extend(job.get("results", []))
            return all_data

    def stop_job(self, job_id: str) -> bool:
        """Stop a running job."""
        if job_id in self.jobs and self.jobs[job_id]["status"] == "running":
            self.jobs[job_id]["status"] = "stopped"
            self.jobs[job_id]["completed_at"] = datetime.now().isoformat()
            logging.info(f"Job {job_id} stopped by user")
            return True
        return False

    def clear_logs(self) -> None:
        """Clear all stored logs."""
        self.logs.clear()
        logging.info("Logs cleared")

    def get_system_status(self) -> Dict[str, Any]:
        """Return system status information."""
        return {
            "scraper_available": self.scraper_available,
            "total_jobs": len(self.jobs),
            "running_jobs": len([j for j in self.jobs.values() if j["status"] == "running"]),
            "completed_jobs": len([j for j in self.jobs.values() if j["status"] == "completed"]),
            "failed_jobs": len([j for j in self.jobs.values() if j["status"] == "failed"]),
            "log_entries": len(self.logs),
            "uptime": "N/A"  # Could track actual uptime if needed
        }
