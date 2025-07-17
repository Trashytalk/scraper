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
