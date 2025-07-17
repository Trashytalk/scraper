# scraper

## Log Streaming

The backend exposes an SSE endpoint to stream log messages in real time.

```
GET /logs/stream
```

Use this route from the frontend to monitor running jobs or debug output.
