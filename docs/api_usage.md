# API Usage

The FastAPI backend exposes several routes for launching scraping tasks and
retrieving results. The examples below assume the API is running locally on
`http://localhost:8000`.

## Health Check

```bash
curl http://localhost:8000/
```

## Start a Scraping Job

```bash
curl -X POST http://localhost:8000/scrape
```

The response contains a `task_id` which can be polled for status.

## Check Task Status

```bash
curl http://localhost:8000/tasks/<task_id>
```

## View Scraped Data

```bash
curl http://localhost:8000/data
```

## Job Information

List all known jobs:

```bash
curl http://localhost:8000/jobs
```

Query a single job:

```bash
curl http://localhost:8000/jobs/<task_id>
```

## Real-Time Notifications

Open a WebSocket connection to `/ws/notifications` to receive broadcast
messages from the server. Each connected client will receive any message sent by
another client.

## Log Streaming

Logs can be streamed with Server-Sent Events:

```bash
curl http://localhost:8000/logs/stream
```
