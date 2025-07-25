# Centralized Logging

This project writes JSON logs to `business_intel_scraper/backend/logs/app.log` by default. Logs can also be forwarded to an external service for aggregation.

## Environment Variables

- `LOG_FORWARD_URL` – optional HTTP endpoint that receives each log entry as JSON. When set, the `setup_logging` helper posts log records to this URL in addition to writing to the local file.
- `LOG_LEVEL` – standard logging level (e.g. `INFO` or `DEBUG`).

Add these variables to your `.env` file and restart the API and workers to enable forwarding.

## Example ELK Stack

An easy way to aggregate logs is with the Elastic Stack (Elasticsearch, Logstash, Kibana). A minimal Logstash configuration that accepts the forwarded logs looks like:

```logstash
input {
  http {
    host => "0.0.0.0"
    port => 8080
  }
}

output {
  elasticsearch {
    hosts => ["http://localhost:9200"]
    index => "bi-scraper-logs-%{+YYYY.MM.dd}"
  }
}
```

Run Elasticsearch and Kibana using the official Docker images and start Logstash with the above pipeline. Set `LOG_FORWARD_URL=http://localhost:8080` for both the API service and any Celery workers. All JSON logs will then appear in Kibana.

Prometheus remains responsible for metrics. Configure it to scrape `/metrics` from the API and any exporters as shown in `infra/monitoring/README.md`.

## Collecting Logs

Logs from the FastAPI server and Celery workers are written to `business_intel_scraper/backend/logs/app.log`.
If `LOG_FORWARD_URL` is configured they are also sent to the remote endpoint.

To inspect logs locally run:

```bash
tail -f business_intel_scraper/backend/logs/app.log
```

You can also stream logs over SSE from the API:

```bash
curl http://localhost:8000/logs/stream
```

Start a worker with:

```bash
celery -A business_intel_scraper.backend.workers.tasks.celery_app worker --loglevel=info
```

Ensure the environment variables above are set for both the API and worker so log records are forwarded correctly.
