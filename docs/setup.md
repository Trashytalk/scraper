# Setup

These instructions describe how to configure the project locally and run all services.

## Prerequisites

- Python 3.11+
- Node.js (for the optional frontend)
- Docker and Docker Compose (for the full stack example)

Clone the repository and create a virtual environment:

```bash
git clone <repo-url>
cd scraper
python -m venv .venv
source .venv/bin/activate
```

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

Copy the sample environment file and adjust values as needed:

```bash
cp .env.example .env
```

Install frontend dependencies (optional):

```bash
cd business_intel_scraper/frontend
npm install
cd ../../
```

## Running the full stack with Docker Compose

The repository ships with a `docker-compose.yml` in `business_intel_scraper/`.
It starts the FastAPI backend and a Celery worker. Redis must be available for
Celery. The quickest way to launch everything is:

```bash
docker run -d -p 6379:6379 --name redis redis:7
cd business_intel_scraper
docker compose up --build
```

The API will be available on [http://localhost:8000](http://localhost:8000).
To serve the frontend, start its dev server in another terminal:

```bash
cd business_intel_scraper/frontend
npm start
```

You can now access the dashboard on [http://localhost:8000](http://localhost:8000)
to monitor jobs and view results in real time while the backend handles API requests.
