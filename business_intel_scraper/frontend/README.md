# Frontend Development Setup

This directory holds a minimal frontend application. The only dependency is listed in `package.json`, but running `npm install` ensures all Node modules are present.

## Install Node dependencies

```bash
npm install
```

## Start the development server

Use the following command to serve the `public` folder locally.

```bash
npm start
```

The server runs on [http://localhost:8000](http://localhost:8000) by default.

## Building and running

No build step is required. The development server simply serves the files from
the `public` directory. Install dependencies once and then start the server:

```bash
npm install
npm start
```

During development the frontend expects the FastAPI backend to be running on the
same host and port. Start the API with `uvicorn` or via Docker Compose and then
open [http://localhost:8000](http://localhost:8000) in your browser.

The application communicates with the backend using the REST endpoints defined
in `docs/api_usage.md` and listens for real time updates on the
`/ws/notifications` WebSocket and `/logs/stream` SSE endpoint.
