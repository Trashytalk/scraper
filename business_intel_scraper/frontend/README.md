# Frontend Development Guide

[![Security Hardened](https://img.shields.io/badge/security-hardened%20%E2%9C%85-green)](../../SECURITY_ROTATION_PLAYBOOK.md)
[![Version](https://img.shields.io/badge/version-2.0.1--security-orange)](../../IMPLEMENTATION_SUMMARY_REPORT.md)

The frontend is now a modern React application with real-time capabilities built with Vite and Tailwind CSS.

## 🛡️ **Security Notice (August 2025)**

**Security hardening completed:**
- ✅ All exposed credentials eliminated and rotated
- ✅ Pre-commit security scanning active
- ✅ CI/CD vulnerability blocking enabled
- ✅ Clean security validation passed

## Quick Start

### Prerequisites

- Node.js 16+ and npm
- Backend API running on port 8000

### Development Setup

1. **Quick Start (Recommended)**:
   ```bash
   cd business_intel_scraper/frontend
   ./frontend.sh dev
   ```

2. **Manual Setup**:
   ```bash
   cd business_intel_scraper/frontend
   npm install
   npm run dev
   ```

The frontend will be available at `http://localhost:3000` with automatic proxy to the backend API.

## Features

### 🎛️ Real-time Dashboard

- Live job monitoring with WebSocket updates
- Interactive charts showing scraping metrics
- Status indicators for system health
- Real-time notifications

### 📊 Data Visualization

- Job success rate tracking
- Activity timeline charts
- Performance metrics
- Export capabilities (CSV/JSON)

### 🎨 Modern UI/UX

- Responsive design with Tailwind CSS
- Professional component library
- Loading states and animations
- Mobile-friendly interface

## Available Scripts

The `frontend.sh` script provides convenient commands:

- `./frontend.sh install` - Install dependencies
- `./frontend.sh dev` - Start development server
- `./frontend.sh build` - Build for production
- `./frontend.sh preview` - Preview production build
- `./frontend.sh help` - Show all commands

## Technology Stack

- **React 18**: Modern React with hooks
- **Vite**: Fast development and build tool
- **Tailwind CSS**: Utility-first styling
- **Recharts**: Data visualization
- **React Query**: Data fetching
- **WebSocket**: Real-time updates

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
