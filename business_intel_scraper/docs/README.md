# Documentation

This folder contains developer documentation and examples. The NLP module now
includes basic text-cleaning helpers for stripping HTML tags and normalizing
whitespace. See `business_intel_scraper.backend.nlp.cleaning` for details.

## Rate Limiting

The API applies a simple in-memory rate limiter. Configure limits using the
``RATE_LIMIT`` and ``RATE_LIMIT_WINDOW`` environment variables.
