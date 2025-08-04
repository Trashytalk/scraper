# Docker setup

This folder contains Dockerfiles for the API server and Celery worker.
A `docker-compose.yml` is provided for local development.

## Usage

Build the images and start the stack:

```bash

cd business_intel_scraper/infra/docker
docker compose up --build

```

The API will be available on `http://localhost:8000`.
