# Monitoring

This directory contains utilities for collecting and exposing
metrics from the scraping platform.

## Prometheus Exporter

`prometheus_exporter.py` runs a small HTTP server on port `8000`
that exposes example metrics in Prometheus format. Run it with:

```bash
python prometheus_exporter.py
```

Prometheus can then scrape `http://localhost:8000/metrics`.

### Scraping the API

When the FastAPI server is running it exposes metrics at `/metrics`.
Configure Prometheus with a scrape config similar to:

```yaml
scrape_configs:
  - job_name: bi-scraper
    static_configs:
      - targets: ['localhost:8000']
```

Metrics from background workers and HTTP endpoints will then be
collected automatically.
