# Business Intelligence Scraper

This project provides a modular framework for scraping and analyzing business intelligence data.

## API

The backend is built with FastAPI and exposes a simple health check at `/`.
Production deployments should enable HTTPS and can configure request rate
limits via environment variables.
Proxy rotation should be enabled to avoid blocking when scraping at scale.

### WebSocket Notifications

Real-time notifications are available via a WebSocket endpoint at `/ws/notifications`. Messages sent by any connected client are broadcast to all clients.

## Configuration

Copy `.env.example` to `.env` and update the values as needed. The application
recognizes the following settings:

```
API_KEY=your_api_key_here
DATABASE_URL=sqlite:///data.db
PROXY_URL=
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

# scraper

## Log Streaming

The backend exposes an SSE endpoint to stream log messages in real time.

```
GET /logs/stream
```

Use this route from the frontend to monitor running jobs or debug output.

This project contains various modules for business intelligence scraping.
The NLP backend now provides text-cleaning helpers for stripping HTML and
normalizing whitespace.

## Database Migrations

Alembic is used to manage schema versions. To apply migrations run:

```bash
cd business_intel_scraper/backend/db
PYTHONPATH=../../.. alembic upgrade head
```

The command uses `alembic.ini` (or `DATABASE_URL`) to connect to the
database and upgrades it to the latest schema.

## Development

Formatting and linting are handled by **black** and **ruff**. Install both
tools and run them from the repository root before committing changes.

```bash
pip install black ruff

black .
ruff .
```

Use `ruff --fix .` to automatically apply suggested fixes.

## Installation

1. Create and activate a Python virtual environment.
2. Install the main dependencies:
   ```bash
   pip install fastapi uvicorn celery sqlalchemy scrapy httpx spacy
   ```
   Additional packages may be required depending on your use case.

## Environment Variables

Configuration values are read from environment variables or an optional `.env` file in `business_intel_scraper/`.
Common settings include:

- `API_KEY` – credentials for external APIs.
- `DATABASE_URL` – SQLAlchemy connection string (default `sqlite:///data.db`).
- `PROXY_URL` – proxy server address if scraping through a proxy.
- `CELERY_BROKER_URL` – broker URL for Celery tasks (`redis://localhost:6379/0` by default).
- `CELERY_RESULT_BACKEND` – result backend for Celery (defaults to the broker URL).
- `ALLOWED_ORIGINS` – comma-separated list of origins allowed for CORS (default `*`).

## Running the Server

Start the FastAPI app with Uvicorn:

```bash
uvicorn business_intel_scraper.backend.api.main:app --reload
```

If background tasks are used, run a Celery worker in a separate terminal:

```bash
celery -A business_intel_scraper.backend.workers.tasks.celery_app worker --loglevel=info
```

