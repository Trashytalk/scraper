# Workflow

The following steps describe a typical development and execution cycle for the Business Intelligence Scraper.

1. **Install dependencies**
   - Create a virtual environment and run `pip install -r requirements.txt`.
   - Copy `.env.example` to `.env` and adjust settings.
2. **Start services**
   - Ensure Redis is running.
   - Launch the API with `uvicorn business_intel_scraper.backend.api.main:app`.
   - Start a Celery worker with `celery -A business_intel_scraper.backend.workers.tasks.celery_app worker`.
   - Optional: run Celery beat to execute scheduled jobs.
3. **Queue a job**
   - Send `POST /scrape` or use `python -m business_intel_scraper.cli scrape`.
   - The response contains a task identifier.
4. **Monitor progress**
   - Poll `/tasks/<id>` for status updates.
   - Stream logs from `/logs/stream` or connect to `/ws/notifications` for real‑time events.
   - Metrics are available at `/metrics`.
5. **Retrieve results**
   - Call `/data` or `/export?format=csv` to download scraped items.
   - The CLI also supports `status` and `download` commands.
6. **Extend the platform**
   - Add spiders in `backend/modules/crawlers` and their tasks in `backend/workers/tasks.py`.
   - Update the database models or pipelines as needed and run Alembic migrations.

For containerised setups start Redis, the API and a worker with `docker compose up` from the `business_intel_scraper` directory.  See `docs/deployment.md` for production deployment notes.
