# 🔍 Business Intelligence Scraper

> **A comprehensive, modular framework for collecting and analyzing business intelligence data from web sources and OSINT tools.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 🚀 Quick Start

### One-Command Setup
```bash
# Clone and setup everything automatically
git clone https://github.com/Trashytalk/scraper.git
cd scraper
./setup.sh

# Run the demo
./demo.sh
```

**🎯 [Complete Quick Start Guide](QUICKSTART.md)**

## 🎪 **Project Templates**

Create specialized projects with pre-configured templates:

```bash
# Business research project
./create-project.sh business-research my-research

# Competitor analysis
./create-project.sh competitor-analysis acme-analysis

# Security audit (OSINT)
./create-project.sh security-audit pentest-recon

# Development/testing
./create-project.sh development test-project
```

| **Template** | **Use Case** | **Features** |
|-------------|-------------|-------------|
| `business-research` | Market analysis, due diligence | Company data, financials, news monitoring |
| `competitor-analysis` | Competitive intelligence | Pricing tracking, product analysis, positioning |
| `security-audit` | OSINT, penetration testing | Domain recon, vulnerability assessment |
| `development` | Testing, prototyping | Fast setup, mock data, debugging tools |

That's it! The demo will start the API server and run an example scraper. Visit `http://localhost:8000` to see the dashboard.

## ✨ Key Features

- **🕷️ Multi-Engine Scraping**: Scrapy spiders + Playwright browser automation
- **🌐 Web Dashboard**: Real-time job monitoring and data visualization  
- **⚡ Async Processing**: Celery task queue with Redis backend
- **🔌 OSINT Integrations**: SpiderFoot, theHarvester, Shodan, Nmap, and more
- **🗃️ Flexible Storage**: SQLite, PostgreSQL, MySQL support
- **📊 Built-in Analytics**: NLP processing, geolocation, entity extraction
- **🛡️ Production Ready**: JWT auth, rate limiting, monitoring, Docker deployment
- **🎯 Industry Templates**: Pre-configured workflows for common use cases

## 📋 Use Cases

| Use Case | Description | Example Spiders |
|----------|-------------|----------------|
| **Due Diligence** | Company verification and background checks | Company registries, business listings |
| **Competitor Analysis** | Market research and competitive intelligence | News feeds, social media, tech stacks |
| **Supply Chain Mapping** | Vendor and partner discovery | Business directories, procurement databases |
| **Security Research** | Domain analysis and threat intelligence | OSINT tools, subdomain enumeration |
| **Market Research** | Industry trends and opportunity analysis | News scraping, financial data |

## 🏃‍♂️ Quick Examples

### Start a Company Registry Search
```bash
# Activate environment
source .venv/bin/activate

# Search UK Companies House
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{"spider": "national_company_registry", "country": "uk"}'
```

### Run OSINT Scan
```bash
# Subdomain enumeration
curl -X POST http://localhost:8000/osint/subfinder \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com"}'
```

### Export Data
```bash
# Export as CSV
curl "http://localhost:8000/export?format=csv" > companies.csv

# Export as JSON
curl "http://localhost:8000/export?format=json" > companies.json
```

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
2. Install the framework along with its dependencies:
   ```bash
   pip install .
   ```
   For editable development installs use `pip install -e .`.
   The optional frontend requires Node.js. Run `npm install` inside
   `business_intel_scraper/frontend` to enable the real-time dashboard.
3. Copy `.env.example` to `.env` and adjust values to match your environment.

## Environment Variables

Configuration values are read from environment variables or an optional `.env` file in `business_intel_scraper/`.
Common settings include:

- `API_KEY` – credentials for external APIs.
- `GOOGLE_API_KEY` – API key for Google geocoding.
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
- `LOG_FORWARD_URL` – optional HTTP endpoint to forward JSON logs.
- `LOG_LEVEL` – logging level for the API and workers.

## Request Caching

All outgoing requests made with the `requests` library are cached automatically
when the application starts. Set `CACHE_BACKEND` to `redis` or `filesystem` to
choose the cache store. `CACHE_REDIS_URL`, `CACHE_DIR` and `CACHE_EXPIRE`
control the connection URL, cache directory and expiration time. Using a cache
avoids re-fetching identical URLs during scraping and when obtaining proxies.

## Proxy Configuration

Configure proxy rotation using provider classes. Supply one or more providers to
`ProxyManager` for automatic fallback when a proxy fails. Each proxy is verified
using a lightweight health check so blocked or dead proxies are skipped
automatically. Commercial services can be used via `CommercialProxyAPIProvider`
together with the `PROXY_PROVIDER_ENDPOINTS` and `PROXY_API_KEY` variables.

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
This runs the `scheduled_run_all_spiders` task every day at midnight to launch
all available spiders.

With the services running you can interact with the API:

```bash
curl http://localhost:8000/              # health check
curl -X POST http://localhost:8000/scrape # launch the example spider
```

Task progress can be queried at `/tasks/<task_id>` and log messages stream from `/logs/stream`.

## Workflow

1. Install dependencies and copy `.env.example` to `.env`.
2. Start Redis, then run the API and a Celery worker.
3. Queue jobs via `POST /scrape` or the CLI.
4. Check `/tasks/<id>` and `/logs/stream` to monitor progress.
5. Download results from `/export` or via the CLI once jobs complete.
6. Optional: run Celery beat to execute periodic jobs.

See [docs/workflow.md](docs/workflow.md) for a more detailed walk-through.

### Command Line Client

A small CLI is included for interacting with the API. It defaults to http://localhost:8000 and reads a bearer token from the `BI_SCRAPER_TOKEN` environment variable.

```bash
python -m business_intel_scraper.cli scrape       # launch a job
python -m business_intel_scraper.cli status <id>  # check status
python -m business_intel_scraper.cli download -o results.json
python -m business_intel_scraper.cli export --format csv -o results.csv


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
- **Geocoding helpers** – addresses are geocoded via OpenStreetMap Nominatim or Google when a `GOOGLE_API_KEY` is provided.
- **Frontend dashboard** – a lightweight dashboard displays job progress, logs and scraped results in real time.
- **Additional OSINT tools** – Shodan and Nmap scans are now available as Celery tasks.

Contributions are welcome to help flesh out these areas.


## Desktop GUI

A Python desktop interface is now scaffolded in the `gui/` directory. It uses
PyQt and provides placeholders for a dashboard, job manager, log viewer and data
table. Run the application with:

```bash
python -m gui.main
```

The GUI currently relies on stub implementations. Hook up the components to the
scraper modules to launch and monitor jobs without using the CLI.
