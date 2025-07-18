# Business Intelligence Scraper

This project provides a modular framework for scraping and analyzing business intelligence data.

## Overview
The Business Intelligence Scraper is an experimental platform for collecting business data from the web and open-source intelligence (OSINT) tools. It combines Scrapy-based spiders, optional browser automation, and a FastAPI backend with Celery workers for asynchronous jobs.

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

Use this route from the frontend to monitor running jobs or debug output. Logs
are also written to `business_intel_scraper/backend/logs/app.log`. To forward
them to a centralized collector set `LOG_FORWARD_URL` in your environment and
see [docs/logging.md](docs/logging.md) for an example ELK setup.

## Metrics

Prometheus metrics are available at the `/metrics` endpoint. Run the server and
scrape metrics with Prometheus or `curl`:

```bash
curl http://localhost:8000/metrics
```

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

1. Clone the repository and create a Python virtual environment:
   ```bash
   git clone <repo-url>
   cd scraper
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
   The optional frontend requires Node.js. Run `npm install` inside
   `business_intel_scraper/frontend` if you want the demo UI.
3. Copy `.env.example` to `.env` and adjust values to match your environment.

## Environment Variables

Configuration values are read from environment variables or an optional `.env` file in `business_intel_scraper/`.
Common settings include:

- `API_KEY` – credentials for external APIs.
- `DATABASE_URL` – SQLAlchemy connection string (default `sqlite:///data.db`).
- `PROXY_URL` – proxy server address if scraping through a proxy.
- `PROXY_ROTATE` – set to `true` to rotate proxies on each request.
- `PROXY_PROVIDER_ENDPOINTS` – comma-separated API endpoints for commercial providers.
- `PROXY_API_KEY` – API key used with commercial proxy services.
- `CELERY_BROKER_URL` – broker URL for Celery tasks (`redis://localhost:6379/0` by default).
- `CELERY_RESULT_BACKEND` – result backend for Celery (defaults to the broker URL).
- `ALLOWED_ORIGINS` – comma-separated list of origins allowed for CORS (default `*`).
- `CAPTCHA_API_KEY` – API token for the CAPTCHA solving service (e.g. 2Captcha).
- `CAPTCHA_API_URL` – base URL for the CAPTCHA provider (defaults to `https://2captcha.com`).
- `CACHE_BACKEND` – set to `redis` or `filesystem` to enable request caching.
- `CACHE_REDIS_URL` – Redis connection URL when using the Redis backend.
- `CACHE_DIR` – directory used for the filesystem cache.
- `CACHE_EXPIRE` – cache expiration time in seconds (default `3600`).

## Proxy Configuration

Configure proxy rotation using provider classes. Supply one or more providers to
`ProxyManager` for automatic fallback when a proxy fails. Commercial services
can be used via `CommercialProxyAPIProvider` together with the
`PROXY_PROVIDER_ENDPOINTS` and `PROXY_API_KEY` variables.

## Running the Server

Start the FastAPI app with Uvicorn:

```bash
uvicorn business_intel_scraper.backend.api.main:app --reload
```

If background tasks are used, run a Celery worker in a separate terminal:

```bash
celery -A business_intel_scraper.backend.workers.tasks.celery_app worker --loglevel=info
```
To run scrapes automatically on a schedule, start Celery beat:

```bash
celery -A business_intel_scraper.backend.workers.tasks.celery_app beat --loglevel=info
```

With the services running you can interact with the API:

```bash
curl http://localhost:8000/              # health check
curl -X POST http://localhost:8000/scrape # launch the example spider
```

Task progress can be queried at `/tasks/<task_id>` and log messages stream from `/logs/stream`.

### Command Line Client

A small CLI is included for interacting with the API. It defaults to http://localhost:8000 and reads a bearer token from the BI_SCRAPER_TOKEN environment variable.

```bash
python -m business_intel_scraper.cli scrape       # launch a job
python -m business_intel_scraper.cli status <id>  # check status
python -m business_intel_scraper.cli download -o results.json
```

The repository also provides a `docker-compose.yml` in `business_intel_scraper/` for launching Redis, the API and a worker together:

```bash
docker run -d -p 6379:6379 --name redis redis:7
cd business_intel_scraper
docker compose up --build
```
See `docs/deployment.md` for Kubernetes deployment instructions.

## Third-Party Integrations

Lightweight wrappers for several external scraping projects are available in
`business_intel_scraper.backend.integrations`. They expose helper functions for
running tools like `crawl4ai`, `SecretScraper`, `colly`, `proxy_pool`,
`spiderfoot` and ProjectDiscovery's `katana`. Each wrapper simply invokes the
underlying CLI when present and raises ``NotImplementedError`` if the tool is
missing.

## Roadmap and Incomplete Features

The repository contains working examples for scraping, simple NLP and OSINT tasks, but several pieces are intentionally stubbed out or incomplete:

- **Captcha solving** – `business_intel_scraper.backend.security.captcha` integrates with configurable providers like 2Captcha.
- **Advanced proxy management** – proxy rotation works with simple providers; integration with commercial proxy APIs is planned.
- **Geocoding helpers** – the geocoding pipeline currently returns deterministic coordinates and does not fully use online providers.
- **Full frontend dashboard** – the included frontend is a minimal placeholder meant for development.
- **Additional OSINT tools** – Shodan and Nmap scans are now available as Celery tasks.

Contributions are welcome to help flesh out these areas.

