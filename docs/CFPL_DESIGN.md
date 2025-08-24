# Capture-First, Process-Later (CFPL) Architecture Design

## Executive Summary

This document outlines the transformation of our scraping platform to a **Capture-First, Process-Later (CFPL)** architecture where all fetched content is durably persisted before any processing occurs.

## Architecture Overview

### Storage Model: Content-Addressed Store (CAS)

**Decision**: CAS over WARC for v1 implementation

**Rationale**:
- Superior deduplication (identical content stored once)
- Simpler implementation and debugging
- Better fit for incremental development
- Faster hash-based retrieval
- Easy migration path to WARC later if needed

**Trade-offs**:
- Less standardized than WARC (but we control the full stack)
- Requires custom indexing (vs WARC's CDXJ)
- Not directly compatible with existing web archive tools

### Directory Structure

```
<STORAGE_ROOT>/
  raw/                                 # Immutable evidence-grade zone
    cas/
      sha256/ab/abcd1234...            # Raw response bytes by hash
    runs/
      <run_id>/
        <host>/
          <timestamp>/
            manifest.json              # URL capture metadata
            headers.json               # Request/response headers (redacted)
            dom.mhtml                  # Rendered DOM snapshot (optional)
            har.json                   # Network capture log (optional)
            assets/                    # Asset convenience links → CAS
            media/                     # Media files and playlists → CAS
  derived/                             # Purgeable, replayable zone
    <run_id>/
      pages.parquet                    # Structured page data
      media.parquet                    # Media metadata
      text.jsonl                       # Extracted text content
      search/                          # Search indexes
      ml/                              # ML features
      thumbnails/                      # Generated thumbnails
      transcripts/                     # Audio/video transcripts
  index/
    catalog.sqlite                     # Fast lookup: URL → manifest → CAS objects
    content_index.sqlite               # Content-based search
  config/
    retention.json                     # Retention policies
    processors.json                    # Processing pipeline config
```

### Manifest Schema

Each URL capture produces a `manifest.json`:

```json
{
  "manifest_version": "1.0",
  "url": "https://example.com/page",
  "final_url": "https://example.com/page",
  "fetch_start": "2025-08-18T10:30:00Z",
  "fetch_end": "2025-08-18T10:30:02Z",
  "status": 200,
  "redirects": [
    {"from": "http://example.com/page", "to": "https://example.com/page", "status": 301}
  ],
  "request_headers": {
    "user-agent": "Mozilla/5.0...",
    "accept": "text/html,application/xhtml+xml..."
  },
  "response_headers": {
    "content-type": "text/html; charset=utf-8",
    "content-length": "12345",
    "etag": "\"abc123\"",
    "last-modified": "2025-08-18T08:00:00Z"
  },
  "redacted_headers": ["authorization", "cookie"],
  "content": {
    "sha256": "abcd1234...",
    "size": 12345,
    "content_type": "text/html",
    "encoding": "utf-8"
  },
  "dom_snapshot": {
    "enabled": true,
    "sha256": "efgh5678...",
    "format": "mhtml",
    "size": 15678
  },
  "har_capture": {
    "enabled": true,
    "sha256": "ijkl9012...",
    "size": 8901
  },
  "assets": [
    {
      "url": "https://example.com/style.css",
      "sha256": "mnop3456...",
      "size": 2048,
      "content_type": "text/css",
      "discovered_via": "html_link"
    }
  ],
  "media": [
    {
      "url": "https://example.com/video.mp4",
      "sha256": "qrst7890...",
      "size": 1048576,
      "content_type": "video/mp4",
      "capture_method": "direct_download"
    }
  ],
  "tools": {
    "scraper_version": "2.0.0",
    "browser": "playwright-1.40.0",
    "ffmpeg": "6.0"
  },
  "capture_decisions": {
    "drm_detected": false,
    "geo_blocked": false,
    "rate_limited": false
  },
  "errors": []
}
```

### Data Flow

1. **Single-Touch Capture**:
   - Fetch main response → stream to CAS, compute SHA256
   - Render page if enabled → capture DOM + HAR
   - Discover assets → download concurrently to CAS
   - Detect media → capture playlists + segments
   - Write manifest only after ALL content is persisted

2. **RAW → DERIVED Processing**:
   - Triggered only after manifest is committed
   - Reads exclusively from CAS/manifests
   - **No network access** during processing
   - Outputs tagged with lineage to source manifest

3. **Deduplication**:
   - CAS automatically dedupes identical content
   - Manifests track unique URL captures
   - Index links many URLs to same content hash

### Performance & Storage Sizing

**Expected Load**: 10 URLs/minute sustained, 100 URLs/minute burst
**Concurrency**: 2 per domain, 10 total workers
**Storage Growth**: 
- RAW: ~50MB average per URL (varies by site assets)
- DERIVED: ~10MB per URL (structured data + indexes)
- Deduplication savings: 30-60% typical

**Retention**:
- RAW: 2 years (configurable)
- DERIVED: 90 days (configurable, can be regenerated)

### Security & Access Control

**Filesystem Permissions**:
```
/storage/raw/     - 440 scraper:scraper (read-only after write)
/storage/derived/ - 660 scraper:processors (read-write)
/storage/index/   - 660 scraper:processors (read-write)
```

**Header Redaction**: `Authorization`, `Cookie`, `X-API-Key` removed from logs, preserved in encrypted form if needed for replay

**Audit Trail**: All writes logged with timestamp, tool version, operator

## Implementation Plan

### PR-1: Storage Foundation
- CAS implementation with SHA256 indexing
- Manifest writer with atomic operations
- Configuration system
- Basic CLI for inspection

### PR-2: Capture Engine
- Single-touch URL fetching
- Asset discovery and concurrent download
- Media capture (direct + HLS)
- DOM/HAR capture integration

### PR-3: Processing Pipeline
- Post-capture job scheduler
- HTML→structured data processors
- Media metadata extraction
- Search indexing

### PR-4: Migration & Operations
- Legacy data migration scripts
- Monitoring and metrics
- Operator documentation
- Retention policy enforcement

## Acceptance Criteria

- ✅ **100% capture-before-process**: No parsing starts until RAW write completes
- ✅ **Immutability**: RAW zone is write-once, modification attempts fail
- ✅ **Replayability**: Network-offline reprocessing produces identical DERIVED outputs
- ✅ **Deduplication**: Identical content stored once, properly indexed
- ✅ **Lineage**: Every DERIVED artifact traces to source RAW manifest
- ✅ **Performance**: Sustained 10 URLs/min with <30s latency per URL
