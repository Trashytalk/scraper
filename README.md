# Business Intelligence Scraper

This project provides a modular framework for scraping and analyzing business intelligence data.

## API

The backend is built with FastAPI and exposes a simple health check at `/`.

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
