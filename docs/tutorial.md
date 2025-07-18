# Tutorial: Running Your First Spider

This walkthrough demonstrates how to set up the stack, launch the sample spider, and inspect the results.

## 1. Install prerequisites

- Python 3.11+
- Node.js (optional, for the demo frontend)
- Docker and Docker Compose

Clone the repository and create a virtual environment:

```bash
git clone <repo-url>
cd scraper
python -m venv .venv
source .venv/bin/activate
```

Install dependencies and copy the example environment file:

```bash
pip install -r requirements.txt
cp .env.example .env
```

Install the frontend dependencies if you want to try the UI:

```bash
cd business_intel_scraper/frontend
npm install
cd ../../
```

## 2. Start the stack with Docker

A `docker-compose.yml` in `business_intel_scraper/` starts the API and a Celery worker. Launch Redis and bring up the services:

```bash
docker run -d -p 6379:6379 --name redis redis:7
cd business_intel_scraper
docker compose up --build
```

The API will be available at [http://localhost:8000](http://localhost:8000).

## 3. Launch the example spider

Send a request to the `/scrape` endpoint to start the built-in `ExampleSpider`:

```bash
curl -X POST http://localhost:8000/scrape
```

The response contains a `task_id` that can be used to monitor progress:

```bash
curl http://localhost:8000/tasks/<task_id>
```

You can also use the provided command line helper which defaults to the local API:

```bash
python -m business_intel_scraper.cli scrape
```

## 4. Examine the results

Once the task finishes, fetch the scraped items from the `/data` endpoint:

```bash
curl http://localhost:8000/data
```

With the CLI:

```bash
python -m business_intel_scraper.cli download -o results.json
```

Logs stream in real time from `/logs/stream` and can be viewed in the browser or with `curl`:

```bash
curl http://localhost:8000/logs/stream
```

That's it—you've run a spider and collected its output. Explore the other spiders in `business_intel_scraper/backend/modules/crawlers/spider.py` to expand your scraping jobs.
