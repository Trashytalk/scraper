# Business Intelligence Scraper

This project provides a modular framework for scraping and analyzing business intelligence data.

## API

The backend is built with FastAPI and exposes a simple health check at `/`.

### WebSocket Notifications

Real-time notifications are available via a WebSocket endpoint at `/ws/notifications`. Messages sent by any connected client are broadcast to all clients.
