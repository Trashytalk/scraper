"""Jobs API Endpoints for Job Management."""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel


router = APIRouter(prefix="/jobs", tags=["jobs"])


class JobCreate(BaseModel):
    """Job creation request model."""

    name: str
    url: str
    scraper_type: str
    schedule: str = "manual"
    config: Dict[str, Any] = {}


class BatchJobCreate(BaseModel):
    """Batch job creation from crawler results."""

    base_name: str
    source_crawler_job_id: int
    scraper_type: str
    urls: List[str]
    batch_size: int = 10
    config: Dict[str, Any] = {}


class Job(BaseModel):
    """Job response model."""

    id: int
    name: str
    url: str
    scraper_type: str
    status: str
    progress: int
    created_at: str
    last_run: Optional[str] = None
    next_run: Optional[str] = None
    items_collected: int = 0
    schedule: str = "manual"
    config: Dict[str, Any] = {}


class JobStats(BaseModel):
    """Job statistics model."""

    total_jobs: int
    running_jobs: int
    completed_jobs: int
    failed_jobs: int
    total_items_collected: int


# Global job storage - in production this would be a database
JOBS_STORE: Dict[int, Dict[str, Any]] = {}
NEXT_JOB_ID = 1


def create_initial_jobs():
    """Create some initial jobs if none exist."""
    global NEXT_JOB_ID
    if not JOBS_STORE:
        initial_jobs = [
            {
                "id": 1,
                "name": "News Article Monitoring",
                "url": "https://example-news.com",
                "scraper_type": "news",
                "status": "idle",
                "progress": 0,
                "created_at": "2025-07-22T10:00:00Z",
                "last_run": None,
                "next_run": None,
                "items_collected": 0,
                "schedule": "hourly",
                "config": {},
                "task_id": None,
            },
            {
                "id": 2,
                "name": "E-commerce Product Tracker",
                "url": "https://example-shop.com",
                "scraper_type": "ecommerce",
                "status": "completed",
                "progress": 100,
                "created_at": "2025-07-22T09:00:00Z",
                "last_run": "2025-07-22T11:00:00Z",
                "next_run": None,
                "items_collected": 89,
                "schedule": "manual",
                "config": {},
                "task_id": None,
            },
        ]
        for job in initial_jobs:
            JOBS_STORE[job["id"]] = job
        NEXT_JOB_ID = 3


# Initialize jobs on startup
create_initial_jobs()


@router.get("/", response_model=List[Job])
async def get_jobs() -> List[Job]:
    """Get all jobs."""
    try:
        jobs = []
        for job_data in JOBS_STORE.values():
            try:
                # Validate job data before creating Job model
                if not isinstance(job_data, dict):
                    continue
                if "id" not in job_data or "name" not in job_data:
                    continue
                jobs.append(Job(**job_data))
            except Exception as e:
                # Log invalid job data but don't fail entire request
                print(f"Warning: Invalid job data skipped: {e}")
                continue
        return jobs
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve jobs: {str(e)}"
        )


@router.get("/stats", response_model=JobStats)
async def get_job_stats() -> JobStats:
    """Get job statistics."""
    try:
        jobs = list(JOBS_STORE.values())

        # Validate job data for statistics
        valid_jobs = []
        for job in jobs:
            if isinstance(job, dict) and "status" in job:
                valid_jobs.append(job)

        return JobStats(
            total_jobs=len(valid_jobs),
            running_jobs=len([j for j in valid_jobs if j.get("status") == "running"]),
            completed_jobs=len(
                [j for j in valid_jobs if j.get("status") == "completed"]
            ),
            failed_jobs=len([j for j in valid_jobs if j.get("status") == "failed"]),
            total_items_collected=sum(
                j.get("items_collected", 0)
                for j in valid_jobs
                if isinstance(j.get("items_collected"), int)
            ),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to calculate job statistics: {str(e)}"
        )


@router.post("/", response_model=Job)
async def create_job(job_data: JobCreate) -> Job:
    """Create a new job."""
    try:
        global NEXT_JOB_ID

        # Validate input data
        if not job_data.name or not job_data.name.strip():
            raise HTTPException(status_code=422, detail="Job name cannot be empty")

        if not job_data.url or not job_data.url.strip():
            raise HTTPException(status_code=422, detail="Job URL cannot be empty")

        if not job_data.scraper_type or not job_data.scraper_type.strip():
            raise HTTPException(status_code=422, detail="Scraper type cannot be empty")

        # Validate URL format (basic check)
        if not (
            job_data.url.startswith("http://") or job_data.url.startswith("https://")
        ):
            raise HTTPException(
                status_code=422, detail="URL must start with http:// or https://"
            )

        # Validate scraper type
        valid_scraper_types = [
            "news",
            "ecommerce",
            "social",
            "business",
            "general",
            "test",
        ]
        if job_data.scraper_type not in valid_scraper_types:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid scraper type. Must be one of: {', '.join(valid_scraper_types)}",
            )

        new_job = {
            "id": NEXT_JOB_ID,
            "name": job_data.name.strip(),
            "url": job_data.url.strip(),
            "scraper_type": job_data.scraper_type,
            "status": "idle",
            "progress": 0,
            "created_at": datetime.now().isoformat() + "Z",
            "last_run": None,
            "next_run": None,
            "items_collected": 0,
            "schedule": job_data.schedule,
            "config": job_data.config or {},
            "task_id": None,
        }

        JOBS_STORE[NEXT_JOB_ID] = new_job
        NEXT_JOB_ID += 1

        return Job(**new_job)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create job: {str(e)}")


@router.get("/{job_id}", response_model=Job)
async def get_job(job_id: int) -> Job:
    """Get a specific job by ID."""
    try:
        if not isinstance(job_id, int) or job_id <= 0:
            raise HTTPException(
                status_code=422, detail="Invalid job ID: must be a positive integer"
            )

        if job_id not in JOBS_STORE:
            raise HTTPException(
                status_code=404, detail=f"Job with ID {job_id} not found"
            )

        job_data = JOBS_STORE[job_id]
        if not isinstance(job_data, dict):
            raise HTTPException(status_code=500, detail="Invalid job data format")

        return Job(**job_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve job: {str(e)}")


@router.post("/{job_id}/start")
async def start_job(job_id: int) -> Dict[str, str]:
    """Start a job."""
    try:
        if not isinstance(job_id, int) or job_id <= 0:
            raise HTTPException(
                status_code=422, detail="Invalid job ID: must be a positive integer"
            )

        if job_id not in JOBS_STORE:
            raise HTTPException(
                status_code=404, detail=f"Job with ID {job_id} not found"
            )

        job = JOBS_STORE[job_id]

        # Validate job data
        if not isinstance(job, dict):
            raise HTTPException(status_code=500, detail="Invalid job data format")

        # Prevent starting already running jobs
        if job.get("status") == "running":
            return {"message": f"Job {job_id} is already running", "status": "running"}

        # Check if job is in a valid state to start
        if job.get("status") == "failed":
            # Reset failed jobs before starting
            job["status"] = "idle"

        # Launch the actual scraping task
        task_id = str(uuid.uuid4())

        # Update job status
        job["status"] = "running"
        job["progress"] = 0
        job["last_run"] = datetime.now().isoformat() + "Z"
        job["task_id"] = task_id
        job["items_collected"] = 0

        # Start background task (simplified version)
        # In a real implementation, this would launch a Celery task
        # task_result = launch_scraping_task.delay(job["url"], job["config"])
        # job["task_id"] = task_result.id

        return {
            "message": f"Job {job_id} started successfully",
            "task_id": task_id,
            "status": "running",
        }

    except HTTPException:
        raise
    except Exception as e:
        # Reset job status on error
        if job_id in JOBS_STORE:
            JOBS_STORE[job_id]["status"] = "failed"
        raise HTTPException(status_code=500, detail=f"Failed to start job: {str(e)}")


@router.post("/{job_id}/stop")
async def stop_job(job_id: int) -> Dict[str, str]:
    """Stop a job."""
    try:
        if not isinstance(job_id, int) or job_id <= 0:
            raise HTTPException(
                status_code=422, detail="Invalid job ID: must be a positive integer"
            )

        if job_id not in JOBS_STORE:
            raise HTTPException(
                status_code=404, detail=f"Job with ID {job_id} not found"
            )

        job = JOBS_STORE[job_id]

        # Validate job data
        if not isinstance(job, dict):
            raise HTTPException(status_code=500, detail="Invalid job data format")

        # Check if job is running
        if job.get("status") != "running":
            return {
                "message": f"Job {job_id} is not currently running",
                "status": job.get("status", "unknown"),
            }

        # Stop the job
        job["status"] = "stopped"
        job["progress"] = job.get("progress", 0)  # Keep current progress

        # In a real implementation, this would stop the Celery task
        # if job.get("task_id"):
        #     revoke(job["task_id"], terminate=True)

        return {"message": f"Job {job_id} stopped successfully", "status": "stopped"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop job: {str(e)}")


@router.delete("/{job_id}")
async def delete_job(job_id: int) -> Dict[str, str]:
    """Delete a job."""
    try:
        if not isinstance(job_id, int) or job_id <= 0:
            raise HTTPException(
                status_code=422, detail="Invalid job ID: must be a positive integer"
            )

        if job_id not in JOBS_STORE:
            raise HTTPException(
                status_code=404, detail=f"Job with ID {job_id} not found"
            )

        job = JOBS_STORE[job_id]

        # Validate job data
        if not isinstance(job, dict):
            raise HTTPException(status_code=500, detail="Invalid job data format")

        # Stop the job if it's running
        if job.get("status") == "running":
            # In a real implementation, this would revoke the Celery task
            if job.get("task_id"):
                # celery_app.control.revoke(job["task_id"], terminate=True)
                pass

        # Remove from store
        del JOBS_STORE[job_id]

        return {"message": f"Job {job_id} deleted successfully", "status": "deleted"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete job: {str(e)}")


@router.get("/{job_id}/logs")
async def get_job_logs(
    job_id: int, limit: int = Query(default=100, ge=1, le=1000)
) -> Dict[str, Any]:
    """Get logs for a specific job."""
    if job_id not in JOBS_STORE:
        raise HTTPException(status_code=404, detail="Job not found")

    job = JOBS_STORE[job_id]

    # Generate realistic logs based on job status and type
    logs = []
    current_time = datetime.now()

    if job["status"] == "running":
        logs = [
            {
                "timestamp": (current_time).isoformat() + "Z",
                "level": "INFO",
                "message": f"Job {job_id}: Currently processing {job['url']}",
            },
            {
                "timestamp": (current_time).isoformat() + "Z",
                "level": "INFO",
                "message": f"Job {job_id}: Collected {job['items_collected']} items so far",
            },
            {
                "timestamp": (current_time).isoformat() + "Z",
                "level": "INFO",
                "message": f"Job {job_id}: Progress: {job['progress']}%",
            },
        ]
    elif job["status"] == "completed":
        logs = [
            {
                "timestamp": job.get("last_run", current_time.isoformat() + "Z"),
                "level": "INFO",
                "message": f"Job {job_id}: Successfully completed",
            },
            {
                "timestamp": job.get("last_run", current_time.isoformat() + "Z"),
                "level": "INFO",
                "message": f"Job {job_id}: Total items collected: {job['items_collected']}",
            },
        ]
    elif job["status"] == "failed":
        logs = [
            {
                "timestamp": job.get("last_run", current_time.isoformat() + "Z"),
                "level": "ERROR",
                "message": f"Job {job_id}: Job failed due to connection timeout",
            },
            {
                "timestamp": job.get("last_run", current_time.isoformat() + "Z"),
                "level": "WARNING",
                "message": f"Job {job_id}: Retrying in 5 minutes",
            },
        ]
    else:
        logs = [
            {
                "timestamp": job["created_at"],
                "level": "INFO",
                "message": f"Job {job_id}: Created and ready to start",
            }
        ]

    return {"job_id": job_id, "logs": logs[:limit], "total_logs": len(logs)}


@router.get("/{job_id}/data")
async def get_job_data(
    job_id: int, format: str = Query(default="json")
) -> Dict[str, Any]:
    """Get collected data for a specific job."""
    if job_id not in JOBS_STORE:
        raise HTTPException(status_code=404, detail="Job not found")

    job = JOBS_STORE[job_id]

    # Generate realistic data export info
    data_size = (
        f"{job['items_collected'] * 2.4:.1f} MB"
        if job["items_collected"] > 0
        else "0 MB"
    )

    return {
        "job_id": job_id,
        "format": format,
        "download_url": f"/jobs/{job_id}/download?format={format}",
        "size": data_size,
        "record_count": job["items_collected"],
        "last_updated": job.get("last_run"),
        "status": job["status"],
    }


@router.get("/{job_id}/download")
async def download_job_data(
    job_id: int, format: str = Query(default="json")
) -> Dict[str, Any]:
    """Download collected data for a specific job."""
    if job_id not in JOBS_STORE:
        raise HTTPException(status_code=404, detail="Job not found")

    job = JOBS_STORE[job_id]

    # Generate sample scraped data based on job type
    sample_data = []

    if job["scraper_type"] == "news":
        sample_data = [
            {
                "id": i,
                "title": f"Sample News Article {i}",
                "url": f"{job['url']}/article/{i}",
                "content": f"This is sample content for article {i}",
                "published_date": datetime.now().isoformat(),
                "author": f"Author {i}",
            }
            for i in range(1, min(job["items_collected"] + 1, 10))
        ]
    elif job["scraper_type"] == "ecommerce":
        sample_data = [
            {
                "id": i,
                "product_name": f"Sample Product {i}",
                "price": f"${19.99 + i}",
                "url": f"{job['url']}/product/{i}",
                "description": f"Description for product {i}",
                "in_stock": i % 2 == 0,
            }
            for i in range(1, min(job["items_collected"] + 1, 10))
        ]
    else:
        sample_data = [
            {
                "id": i,
                "url": f"{job['url']}/page/{i}",
                "title": f"Sample Page {i}",
                "content": f"Sample content from page {i}",
                "scraped_at": datetime.now().isoformat(),
            }
            for i in range(1, min(job["items_collected"] + 1, 10))
        ]

    return {
        "job_id": job_id,
        "data": sample_data,
        "total_records": job["items_collected"],
        "format": format,
        "exported_at": datetime.now().isoformat(),
    }


@router.post("/batch", response_model=List[Job])
async def create_batch_jobs(batch_data: BatchJobCreate) -> List[Job]:
    """Create multiple scraping jobs from crawler results."""
    try:
        global NEXT_JOB_ID

        if not batch_data.urls:
            raise HTTPException(
                status_code=400, detail="No URLs provided for batch job creation"
            )

        # Create batches of URLs
        batches = []
        for i in range(0, len(batch_data.urls), batch_data.batch_size):
            batches.append(batch_data.urls[i : i + batch_data.batch_size])

        created_jobs = []

        for i, batch_urls in enumerate(batches):
            job_id = NEXT_JOB_ID
            NEXT_JOB_ID += 1

            # Create job configuration
            job_config = batch_data.config.copy()
            job_config.update(
                {
                    "batch_mode": True,
                    "batch_urls": batch_urls,
                    "source_crawler_job_id": batch_data.source_crawler_job_id,
                    "batch_index": i + 1,
                    "total_batches": len(batches),
                }
            )

            job = {
                "id": job_id,
                "name": f"{batch_data.base_name} - Batch {i + 1}/{len(batches)}",
                "url": batch_urls[0],  # Primary URL
                "scraper_type": batch_data.scraper_type,
                "status": "pending",
                "progress": 0,
                "created_at": datetime.now().isoformat(),
                "last_run": None,
                "next_run": None,
                "items_collected": 0,
                "schedule": "manual",
                "config": job_config,
            }

            JOBS_STORE[job_id] = job
            created_jobs.append(Job(**job))

        return created_jobs

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create batch jobs: {str(e)}"
        )


@router.put("/{job_id}/results")
async def update_job_results(
    job_id: int, results_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Update a job with its crawling/scraping results."""
    try:
        if job_id not in JOBS_STORE:
            raise HTTPException(status_code=404, detail="Job not found")

        job = JOBS_STORE[job_id]

        # Update job with results data
        job["results_data"] = results_data.get("data", [])
        job["status"] = "completed"
        job["completion_time"] = datetime.now().isoformat()
        job["items_collected"] = (
            len(job["results_data"]) if isinstance(job["results_data"], list) else 1
        )

        # Update the job in the store
        JOBS_STORE[job_id] = job

        return {
            "job_id": job_id,
            "status": job["status"],
            "items_collected": job["items_collected"],
            "completion_time": job["completion_time"],
            "message": "Job results updated successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update job results: {str(e)}"
        )


@router.get("/{job_id}/extract-urls")
async def extract_urls_from_job(job_id: int) -> Dict[str, Any]:
    """Extract URLs from a completed crawler job for use in batch scraping."""
    try:
        if job_id not in JOBS_STORE:
            raise HTTPException(status_code=404, detail="Job not found")

        job = JOBS_STORE[job_id]

        if job.get("status") != "completed":
            raise HTTPException(
                status_code=400, detail="Job must be completed to extract URLs"
            )

        # Try to extract URLs from actual job results if available
        extracted_urls = []

        # Check if the job has stored results data
        if "results_data" in job and job["results_data"]:
            results_data = job["results_data"]
            if isinstance(results_data, list):
                for item in results_data:
                    if isinstance(item, dict):
                        # Check common URL fields
                        url_fields = [
                            "url",
                            "link",
                            "href",
                            "page_url",
                            "discovered_url",
                            "target_url",
                            "source_url",
                            "canonical_url",
                            "original_url",
                            "crawled_url",
                            "found_url",
                            "extracted_url",
                            "site_url",
                            "web_url",
                            "full_url",
                        ]

                        for field in url_fields:
                            if field in item and isinstance(item[field], str):
                                url = item[field]
                                if url.startswith(("http://", "https://")):
                                    extracted_urls.append(url)
                                    break

                        # Check for links arrays
                        if "links" in item and isinstance(item["links"], list):
                            for link in item["links"]:
                                if isinstance(link, str) and link.startswith(
                                    ("http://", "https://")
                                ):
                                    extracted_urls.append(link)
                                elif isinstance(link, dict):
                                    for field in url_fields:
                                        if field in link and isinstance(
                                            link[field], str
                                        ):
                                            if link[field].startswith(
                                                ("http://", "https://")
                                            ):
                                                extracted_urls.append(link[field])
                                                break

        # If no real data available, generate sample URLs based on the job
        if not extracted_urls:
            base_url = job.get("url", "https://example.com")

            # Try to extract domain from base URL
            try:
                from urllib.parse import urlparse

                parsed = urlparse(base_url)
                domain = f"{parsed.scheme}://{parsed.netloc}"
            except:
                domain = base_url

            # Generate more realistic sample URLs based on job type
            job_type = job.get("scraper_type", "basic")
            items_count = min(job.get("items_collected", 0), 50)

            if job_type == "e_commerce":
                url_patterns = [
                    "/products/",
                    "/category/",
                    "/shop/",
                    "/item/",
                    "/product-details/",
                    "/collections/",
                    "/catalog/",
                    "/store/",
                ]
            elif job_type == "news":
                url_patterns = [
                    "/articles/",
                    "/news/",
                    "/story/",
                    "/post/",
                    "/blog/",
                    "/category/",
                    "/section/",
                    "/archive/",
                ]
            elif job_type == "social_media":
                url_patterns = [
                    "/profile/",
                    "/user/",
                    "/post/",
                    "/status/",
                    "/tweet/",
                    "/page/",
                    "/group/",
                    "/community/",
                ]
            else:
                url_patterns = [
                    "/page/",
                    "/content/",
                    "/section/",
                    "/article/",
                    "/info/",
                    "/details/",
                    "/view/",
                    "/item/",
                ]

            # Generate sample URLs
            for i in range(1, max(items_count, 10) + 1):
                for pattern in url_patterns[:3]:  # Use first 3 patterns
                    if len(extracted_urls) < 30:  # Limit to 30 URLs
                        extracted_urls.append(f"{domain}{pattern}{i}")

            # Add some category/section URLs
            for i, pattern in enumerate(url_patterns[3:6], 1):
                if len(extracted_urls) < 35:
                    extracted_urls.append(f"{domain}{pattern}category-{i}")

        # Remove duplicates and validate URLs
        unique_urls = []
        seen = set()

        for url in extracted_urls:
            if url not in seen:
                try:
                    # Basic URL validation
                    if url.startswith(("http://", "https://")) and "." in url:
                        unique_urls.append(url)
                        seen.add(url)
                except:
                    continue

        return {
            "job_id": job_id,
            "job_name": job.get("name"),
            "extracted_urls": unique_urls[:50],  # Limit to 50 URLs
            "total_urls": len(unique_urls),
            "extraction_method": (
                "real_data" if job.get("results_data") else "generated_sample"
            ),
            "extraction_time": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract URLs: {str(e)}")
