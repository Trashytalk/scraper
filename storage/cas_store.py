"""
Content-Addressed Store (CAS) Implementation
Provides immutable, hash-based storage for captured web content
"""

import hashlib
import json
import os
import shutil
import sqlite3
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import logging

logger = logging.getLogger(__name__)


class CASStore:
    """Content-Addressed Store for immutable web capture storage"""

    def __init__(self, storage_root: str):
        self.storage_root = Path(storage_root)
        self.cas_root = self.storage_root / "raw" / "cas" / "sha256"
        self.runs_root = self.storage_root / "raw" / "runs"
        self.derived_root = self.storage_root / "derived"
        self.index_root = self.storage_root / "index"
        
        # Ensure directory structure exists
        self._init_storage()
        
        # Initialize catalog database
        self.catalog_db = self.index_root / "catalog.sqlite"
        self._init_catalog()

    def _init_storage(self):
        """Initialize the storage directory structure"""
        for path in [self.cas_root, self.runs_root, self.derived_root, self.index_root]:
            path.mkdir(parents=True, exist_ok=True)

    def _init_catalog(self):
        """Initialize the catalog database for fast lookups"""
        conn = sqlite3.connect(self.catalog_db)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS captures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                final_url TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                run_id TEXT NOT NULL,
                host TEXT NOT NULL,
                status INTEGER NOT NULL,
                content_sha256 TEXT NOT NULL,
                content_type TEXT,
                content_size INTEGER,
                manifest_path TEXT NOT NULL,
                has_dom_snapshot BOOLEAN DEFAULT FALSE,
                has_har BOOLEAN DEFAULT FALSE,
                asset_count INTEGER DEFAULT 0,
                media_count INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                UNIQUE(url, timestamp, run_id)
            )
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_captures_url ON captures(url)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_captures_sha256 ON captures(content_sha256)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_captures_timestamp ON captures(timestamp)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_captures_run_id ON captures(run_id)
        """)
        
        # Content deduplication tracking
        conn.execute("""
            CREATE TABLE IF NOT EXISTS content_objects (
                sha256 TEXT PRIMARY KEY,
                size INTEGER NOT NULL,
                content_type TEXT,
                first_seen TEXT NOT NULL,
                reference_count INTEGER DEFAULT 0,
                cas_path TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()

    def _compute_sha256(self, data: bytes) -> str:
        """Compute SHA256 hash of data"""
        return hashlib.sha256(data).hexdigest()

    def _get_cas_path(self, sha256_hash: str) -> Path:
        """Get the CAS path for a given SHA256 hash"""
        prefix = sha256_hash[:2]
        return self.cas_root / prefix / sha256_hash

    def store_content(self, data: bytes, content_type: Optional[str] = None) -> str:
        """
        Store content in CAS and return SHA256 hash
        Returns existing hash if content already exists
        """
        sha256_hash = self._compute_sha256(data)
        cas_path = self._get_cas_path(sha256_hash)
        
        # Check if content already exists
        if cas_path.exists():
            # Update reference count
            self._update_reference_count(sha256_hash, increment=1)
            return sha256_hash
            
        # Store new content
        cas_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Atomic write: write to temp file then move
        temp_path = cas_path.with_suffix('.tmp')
        try:
            with open(temp_path, 'wb') as f:
                f.write(data)
            
            # Verify integrity
            with open(temp_path, 'rb') as f:
                verify_hash = self._compute_sha256(f.read())
            
            if verify_hash != sha256_hash:
                temp_path.unlink()
                raise ValueError(f"Hash mismatch: expected {sha256_hash}, got {verify_hash}")
            
            # Atomic move
            temp_path.rename(cas_path)
            
            # Make read-only
            cas_path.chmod(0o444)
            
            # Record in catalog
            self._record_content_object(sha256_hash, len(data), content_type, str(cas_path))
            
            logger.info(f"Stored content with hash {sha256_hash} ({len(data)} bytes)")
            return sha256_hash
            
        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            raise e

    def retrieve_content(self, sha256_hash: str) -> bytes:
        """Retrieve content by SHA256 hash"""
        cas_path = self._get_cas_path(sha256_hash)
        
        if not cas_path.exists():
            raise FileNotFoundError(f"Content not found for hash {sha256_hash}")
        
        with open(cas_path, 'rb') as f:
            content = f.read()
        
        # Verify integrity
        verify_hash = self._compute_sha256(content)
        if verify_hash != sha256_hash:
            raise ValueError(f"Content corruption detected for {sha256_hash}")
        
        return content

    def create_manifest(self, run_id: str, url: str, capture_data: Dict[str, Any]) -> str:
        """
        Create a capture manifest and return the manifest path
        This should only be called after all referenced content is stored in CAS
        """
        timestamp = capture_data.get('fetch_start', datetime.utcnow().isoformat() + 'Z')
        host = self._extract_host(url)
        
        # Create run directory structure
        run_dir = self.runs_root / run_id / host / timestamp.replace(':', '-')
        run_dir.mkdir(parents=True, exist_ok=True)
        
        # Build complete manifest
        manifest = {
            "manifest_version": "1.0",
            "run_id": run_id,
            "url": url,
            "final_url": capture_data.get('final_url', url),
            "fetch_start": capture_data.get('fetch_start'),
            "fetch_end": capture_data.get('fetch_end'),
            "status": capture_data.get('status'),
            "redirects": capture_data.get('redirects', []),
            "request_headers": capture_data.get('request_headers', {}),
            "response_headers": capture_data.get('response_headers', {}),
            "redacted_headers": capture_data.get('redacted_headers', []),
            "content": capture_data.get('content', {}),
            "dom_snapshot": capture_data.get('dom_snapshot'),
            "har_capture": capture_data.get('har_capture'),
            "assets": capture_data.get('assets', []),
            "media": capture_data.get('media', []),
            "tools": capture_data.get('tools', {}),
            "capture_decisions": capture_data.get('capture_decisions', {}),
            "errors": capture_data.get('errors', [])
        }
        
        # Write manifest atomically
        manifest_path = run_dir / "manifest.json"
        temp_manifest = manifest_path.with_suffix('.tmp')
        
        try:
            with open(temp_manifest, 'w') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            
            temp_manifest.rename(manifest_path)
            manifest_path.chmod(0o444)  # Read-only
            
            # Record in catalog
            self._record_capture_manifest(manifest, str(manifest_path))
            
            logger.info(f"Created manifest for {url} in {manifest_path}")
            return str(manifest_path)
            
        except Exception as e:
            if temp_manifest.exists():
                temp_manifest.unlink()
            raise e

    def _extract_host(self, url: str) -> str:
        """Extract hostname from URL"""
        from urllib.parse import urlparse
        return urlparse(url).netloc or "unknown"

    def _record_content_object(self, sha256_hash: str, size: int, content_type: Optional[str], cas_path: str):
        """Record content object in catalog"""
        conn = sqlite3.connect(self.catalog_db)
        try:
            conn.execute("""
                INSERT OR IGNORE INTO content_objects 
                (sha256, size, content_type, first_seen, reference_count, cas_path)
                VALUES (?, ?, ?, ?, 1, ?)
            """, (sha256_hash, size, content_type, datetime.utcnow().isoformat(), cas_path))
            conn.commit()
        finally:
            conn.close()

    def _update_reference_count(self, sha256_hash: str, increment: int):
        """Update reference count for content object"""
        conn = sqlite3.connect(self.catalog_db)
        try:
            conn.execute("""
                UPDATE content_objects 
                SET reference_count = reference_count + ? 
                WHERE sha256 = ?
            """, (increment, sha256_hash))
            conn.commit()
        finally:
            conn.close()

    def _record_capture_manifest(self, manifest: Dict[str, Any], manifest_path: str):
        """Record capture manifest in catalog"""
        conn = sqlite3.connect(self.catalog_db)
        try:
            content = manifest.get('content', {})
            conn.execute("""
                INSERT OR REPLACE INTO captures
                (url, final_url, timestamp, run_id, host, status, content_sha256, 
                 content_type, content_size, manifest_path, has_dom_snapshot, 
                 has_har, asset_count, media_count, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                manifest['url'],
                manifest['final_url'], 
                manifest['fetch_start'],
                manifest['run_id'],
                self._extract_host(manifest['url']),
                manifest['status'],
                content.get('sha256', ''),
                content.get('content_type', ''),
                content.get('size', 0),
                manifest_path,
                bool(manifest.get('dom_snapshot')),
                bool(manifest.get('har_capture')),
                len(manifest.get('assets', [])),
                len(manifest.get('media', [])),
                datetime.utcnow().isoformat()
            ))
            conn.commit()
        finally:
            conn.close()

    def query_captures(self, 
                      url: Optional[str] = None,
                      run_id: Optional[str] = None,
                      since: Optional[datetime] = None,
                      limit: int = 100) -> List[Dict[str, Any]]:
        """Query captured URLs with optional filters"""
        conn = sqlite3.connect(self.catalog_db)
        conn.row_factory = sqlite3.Row
        
        query = "SELECT * FROM captures WHERE 1=1"
        params = []
        
        if url:
            query += " AND url = ?"
            params.append(url)
        
        if run_id:
            query += " AND run_id = ?"
            params.append(run_id)
            
        if since:
            query += " AND timestamp >= ?"
            params.append(since.isoformat())
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        try:
            cursor = conn.execute(query, params)
            results = [dict(row) for row in cursor.fetchall()]
            return results
        finally:
            conn.close()

    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        conn = sqlite3.connect(self.catalog_db)
        
        # Capture statistics
        cursor = conn.execute("SELECT COUNT(*) as total_captures FROM captures")
        total_captures = cursor.fetchone()[0]
        
        cursor = conn.execute("SELECT COUNT(DISTINCT url) as unique_urls FROM captures")
        unique_urls = cursor.fetchone()[0]
        
        cursor = conn.execute("SELECT COUNT(DISTINCT run_id) as total_runs FROM captures")
        total_runs = cursor.fetchone()[0]
        
        # Content statistics
        cursor = conn.execute("""
            SELECT COUNT(*) as total_objects, 
                   SUM(size) as total_bytes,
                   SUM(reference_count) as total_references
            FROM content_objects
        """)
        content_stats = cursor.fetchone()
        
        conn.close()
        
        # Calculate deduplication savings
        total_logical_bytes = total_captures * (content_stats[1] / max(content_stats[0], 1))
        savings_ratio = 1 - (content_stats[1] / max(total_logical_bytes, 1)) if total_logical_bytes > 0 else 0
        
        return {
            "captures": {
                "total": total_captures,
                "unique_urls": unique_urls,
                "total_runs": total_runs
            },
            "storage": {
                "total_objects": content_stats[0],
                "total_bytes": content_stats[1], 
                "total_references": content_stats[2],
                "deduplication_savings": f"{savings_ratio:.1%}"
            },
            "storage_root": str(self.storage_root)
        }

    def cleanup_old_content(self, retention_days: int) -> Dict[str, int]:
        """Clean up old content based on retention policy"""
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        cutoff_str = cutoff_date.isoformat()
        
        conn = sqlite3.connect(self.catalog_db)
        
        # Find old captures
        cursor = conn.execute("""
            SELECT manifest_path FROM captures 
            WHERE timestamp < ?
        """, (cutoff_str,))
        
        old_manifests = [row[0] for row in cursor.fetchall()]
        
        # Delete manifest files and directories
        deleted_manifests = 0
        for manifest_path in old_manifests:
            try:
                path = Path(manifest_path)
                if path.exists():
                    path.unlink()
                    
                # Remove empty directories
                parent = path.parent
                if parent.exists() and not any(parent.iterdir()):
                    parent.rmdir()
                    
                deleted_manifests += 1
            except Exception as e:
                logger.warning(f"Failed to delete manifest {manifest_path}: {e}")
        
        # Remove from catalog
        conn.execute("DELETE FROM captures WHERE timestamp < ?", (cutoff_str,))
        
        # Clean up unreferenced content objects (garbage collection)
        cursor = conn.execute("""
            SELECT co.sha256, co.cas_path 
            FROM content_objects co
            LEFT JOIN captures c ON co.sha256 = c.content_sha256
            WHERE c.content_sha256 IS NULL
        """)
        
        unreferenced_objects = cursor.fetchall()
        deleted_objects = 0
        
        for sha256_hash, cas_path in unreferenced_objects:
            try:
                path = Path(cas_path)
                if path.exists():
                    path.unlink()
                deleted_objects += 1
            except Exception as e:
                logger.warning(f"Failed to delete content object {sha256_hash}: {e}")
        
        # Remove unreferenced objects from catalog
        conn.execute("""
            DELETE FROM content_objects 
            WHERE sha256 NOT IN (
                SELECT DISTINCT content_sha256 FROM captures 
                WHERE content_sha256 != ''
            )
        """)
        
        conn.commit()
        conn.close()
        
        return {
            "deleted_manifests": deleted_manifests,
            "deleted_content_objects": deleted_objects,
            "retention_cutoff": cutoff_str
        }
