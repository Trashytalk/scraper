#!/usr/bin/env python3
"""
CFPL Storage Initialization Script
Creates the Content-Addressed Store structure and catalog database
"""

import json
import os
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional

class CFPLStorageInitializer:
    """Initialize CFPL storage system"""
    
    def __init__(self, storage_root: str = "/home/homebrew/scraper/cfpl_storage"):
        self.storage_root = Path(storage_root)
        
    def initialize_storage(self) -> bool:
        """Initialize complete CFPL storage structure"""
        try:
            print("🚀 Initializing CFPL Storage System...")
            
            # Create directory structure
            self._create_directories()
            
            # Initialize catalog database
            self._initialize_catalog_db()
            
            # Create configuration files
            self._create_config_files()
            
            # Set up permissions
            self._set_permissions()
            
            print("✅ CFPL Storage System initialized successfully!")
            print(f"📁 Storage root: {self.storage_root}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize CFPL storage: {e}")
            return False
    
    def _create_directories(self):
        """Create CFPL directory structure"""
        directories = [
            # Raw storage (immutable)
            "raw/cas/sha256",
            "raw/runs",
            
            # Derived storage (replayable)
            "derived",
            
            # Index storage
            "index",
            
            # Configuration
            "config",
            
            # Temporary processing
            "temp"
        ]
        
        for directory in directories:
            dir_path = self.storage_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created: {directory}")
    
    def _initialize_catalog_db(self):
        """Initialize the catalog SQLite database"""
        db_path = self.storage_root / "index" / "catalog.sqlite"
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create captures table - main URL capture index
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS captures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                final_url TEXT,
                content_sha256 TEXT NOT NULL,
                manifest_path TEXT NOT NULL,
                run_id TEXT,
                host TEXT,
                timestamp TEXT,
                status INTEGER,
                content_type TEXT,
                content_size INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(url, run_id)
            )
        """)
        
        # Create content index - for content-based lookups
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS content_index (
                sha256 TEXT PRIMARY KEY,
                content_type TEXT,
                size INTEGER,
                first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 1
            )
        """)
        
        # Create assets table - for asset relationships
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                capture_id INTEGER,
                asset_url TEXT NOT NULL,
                asset_sha256 TEXT NOT NULL,
                content_type TEXT,
                size INTEGER,
                discovered_via TEXT,
                FOREIGN KEY (capture_id) REFERENCES captures (id)
            )
        """)
        
        # Create run metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY,
                started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                completed_at DATETIME,
                status TEXT DEFAULT 'running',
                total_urls INTEGER DEFAULT 0,
                successful_captures INTEGER DEFAULT 0,
                failed_captures INTEGER DEFAULT 0,
                total_assets INTEGER DEFAULT 0,
                total_size INTEGER DEFAULT 0,
                config_snapshot TEXT
            )
        """)
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_captures_url ON captures(url)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_captures_run_id ON captures(run_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_captures_content_sha256 ON captures(content_sha256)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_content_index_sha256 ON content_index(sha256)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_assets_capture_id ON assets(capture_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_assets_sha256 ON assets(asset_sha256)")
        
        conn.commit()
        conn.close()
        
        print("🗄️ Created catalog database with schema")
    
    def _create_config_files(self):
        """Create default configuration files"""
        config_dir = self.storage_root / "config"
        
        # Retention policy configuration
        retention_config = {
            "version": "1.0",
            "policies": {
                "raw": {
                    "retention_days": 730,  # 2 years
                    "cleanup_frequency": "weekly"
                },
                "derived": {
                    "retention_days": 90,
                    "cleanup_frequency": "daily"
                },
                "temp": {
                    "retention_hours": 24,
                    "cleanup_frequency": "hourly"
                }
            },
            "compression": {
                "enabled": True,
                "threshold_mb": 10,
                "algorithm": "gzip"
            }
        }
        
        with open(config_dir / "retention.json", 'w') as f:
            json.dump(retention_config, f, indent=2)
        
        # Processing pipeline configuration
        processors_config = {
            "version": "1.0",
            "processors": {
                "html_parser": {
                    "enabled": True,
                    "extract_text": True,
                    "extract_links": True,
                    "extract_images": True
                },
                "media_analyzer": {
                    "enabled": True,
                    "extract_metadata": True,
                    "generate_thumbnails": True
                },
                "search_indexer": {
                    "enabled": True,
                    "full_text_search": True,
                    "faceted_search": True
                }
            },
            "concurrency": {
                "max_workers": 4,
                "batch_size": 10
            }
        }
        
        with open(config_dir / "processors.json", 'w') as f:
            json.dump(processors_config, f, indent=2)
        
        # Storage configuration
        storage_config = {
            "version": "1.0",
            "cas": {
                "hash_algorithm": "sha256",
                "compression": "gzip",
                "verification": True
            },
            "manifest": {
                "format_version": "1.0",
                "include_headers": True,
                "include_dom_snapshot": False,
                "include_har_capture": False
            },
            "security": {
                "redact_headers": ["authorization", "cookie", "x-api-key"],
                "encrypt_sensitive": False
            }
        }
        
        with open(config_dir / "storage.json", 'w') as f:
            json.dump(storage_config, f, indent=2)
        
        print("⚙️ Created configuration files")
    
    def _set_permissions(self):
        """Set appropriate file permissions"""
        try:
            # Raw directory - read-only after write (approximated with 755)
            raw_dir = self.storage_root / "raw"
            if raw_dir.exists():
                os.chmod(raw_dir, 0o755)
            
            # Derived and index - read-write
            for subdir in ["derived", "index", "config"]:
                dir_path = self.storage_root / subdir
                if dir_path.exists():
                    os.chmod(dir_path, 0o755)
            
            print("🔒 Set directory permissions")
            
        except Exception as e:
            print(f"⚠️ Could not set permissions: {e}")
    
    def create_sample_data(self):
        """Create sample data for testing the viewer"""
        try:
            print("📝 Creating sample data for testing...")
            
            # Create sample CAS content
            cas_dir = self.storage_root / "raw" / "cas" / "sha256"
            
            # Sample HTML content
            sample_html = """<!DOCTYPE html>
<html>
<head>
    <title>Sample Page</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <h1>Welcome to Sample Page</h1>
    <p>This is a sample page for testing the CFPL viewer.</p>
    <img src="sample-image.jpg" alt="Sample Image">
    <a href="https://example.com/page2">Link to Page 2</a>
</body>
</html>"""
            
            # Sample CSS
            sample_css = """
body { font-family: Arial, sans-serif; margin: 20px; }
h1 { color: #333; }
p { line-height: 1.6; }
"""
            
            # Create content hashes and store in CAS
            import hashlib
            
            html_hash = hashlib.sha256(sample_html.encode()).hexdigest()
            css_hash = hashlib.sha256(sample_css.encode()).hexdigest()
            
            # Store HTML
            html_dir = cas_dir / html_hash[:2]
            html_dir.mkdir(parents=True, exist_ok=True)
            with open(html_dir / html_hash, 'w') as f:
                f.write(sample_html)
            
            # Store CSS
            css_dir = cas_dir / css_hash[:2]
            css_dir.mkdir(parents=True, exist_ok=True)
            with open(css_dir / css_hash, 'w') as f:
                f.write(sample_css)
            
            # Create sample manifest
            run_id = "sample_run_001"
            runs_dir = self.storage_root / "raw" / "runs" / run_id / "example.com"
            runs_dir.mkdir(parents=True, exist_ok=True)
            
            manifest = {
                "manifest_version": "1.0",
                "url": "https://example.com/sample",
                "final_url": "https://example.com/sample",
                "fetch_start": "2025-08-18T10:30:00Z",
                "fetch_end": "2025-08-18T10:30:02Z",
                "status": 200,
                "request_headers": {
                    "user-agent": "CFPL-Scraper/1.0"
                },
                "response_headers": {
                    "content-type": "text/html; charset=utf-8",
                    "content-length": str(len(sample_html))
                },
                "content": {
                    "sha256": html_hash,
                    "size": len(sample_html),
                    "content_type": "text/html",
                    "encoding": "utf-8"
                },
                "assets": [
                    {
                        "url": "https://example.com/style.css",
                        "sha256": css_hash,
                        "size": len(sample_css),
                        "content_type": "text/css",
                        "discovered_via": "html_link"
                    }
                ],
                "tools": {
                    "scraper_version": "1.0.0"
                }
            }
            
            manifest_path = runs_dir / "manifest.json"
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)
            
            # Add to catalog database
            db_path = self.storage_root / "index" / "catalog.sqlite"
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Insert capture record
            cursor.execute("""
                INSERT INTO captures (
                    url, final_url, content_sha256, manifest_path, run_id, 
                    host, timestamp, status, content_type, content_size
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                manifest["url"],
                manifest["final_url"],
                html_hash,
                str(manifest_path.relative_to(self.storage_root)),
                run_id,
                "example.com",
                manifest["fetch_start"],
                manifest["status"],
                "text/html",
                len(sample_html)
            ))
            
            capture_id = cursor.lastrowid
            
            # Insert asset records
            for asset in manifest["assets"]:
                cursor.execute("""
                    INSERT INTO assets (
                        capture_id, asset_url, asset_sha256, content_type,
                        size, discovered_via
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    capture_id,
                    asset["url"],
                    asset["sha256"],
                    asset["content_type"],
                    asset["size"],
                    asset["discovered_via"]
                ))
            
            # Insert content index records
            cursor.execute("""
                INSERT OR IGNORE INTO content_index (sha256, content_type, size)
                VALUES (?, ?, ?)
            """, (html_hash, "text/html", len(sample_html)))
            
            cursor.execute("""
                INSERT OR IGNORE INTO content_index (sha256, content_type, size)
                VALUES (?, ?, ?)
            """, (css_hash, "text/css", len(sample_css)))
            
            # Insert run record
            cursor.execute("""
                INSERT INTO runs (
                    run_id, status, total_urls, successful_captures, 
                    total_assets, total_size
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                run_id, "completed", 1, 1, 1, len(sample_html) + len(sample_css)
            ))
            
            conn.commit()
            conn.close()
            
            print("✅ Sample data created successfully!")
            print(f"📄 Sample URL: {manifest['url']}")
            print(f"🆔 Sample Run ID: {run_id}")
            
        except Exception as e:
            print(f"❌ Failed to create sample data: {e}")
    
    def get_storage_info(self) -> Dict:
        """Get information about the current storage state"""
        try:
            db_path = self.storage_root / "index" / "catalog.sqlite"
            if not db_path.exists():
                return {"error": "Catalog database not found"}
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get capture count
            cursor.execute("SELECT COUNT(*) FROM captures")
            capture_count = cursor.fetchone()[0]
            
            # Get run count
            cursor.execute("SELECT COUNT(*) FROM runs")
            run_count = cursor.fetchone()[0]
            
            # Get content index size
            cursor.execute("SELECT COUNT(*), SUM(size) FROM content_index")
            content_count, total_size = cursor.fetchone()
            
            # Get asset count
            cursor.execute("SELECT COUNT(*) FROM assets")
            asset_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "storage_root": str(self.storage_root),
                "captures": capture_count,
                "runs": run_count,
                "unique_content_items": content_count,
                "total_content_size": total_size or 0,
                "assets": asset_count,
                "cas_directory": str(self.storage_root / "raw" / "cas" / "sha256"),
                "catalog_db": str(db_path)
            }
            
        except Exception as e:
            return {"error": f"Failed to get storage info: {e}"}

def main():
    """CLI interface for CFPL storage initialization"""
    import argparse
    
    parser = argparse.ArgumentParser(description="CFPL Storage Initializer")
    parser.add_argument('--storage-root', default="/home/homebrew/scraper/cfpl_storage",
                       help="CFPL storage root directory")
    parser.add_argument('--with-sample-data', action='store_true',
                       help="Create sample data for testing")
    parser.add_argument('--info', action='store_true',
                       help="Show storage information")
    
    args = parser.parse_args()
    
    initializer = CFPLStorageInitializer(args.storage_root)
    
    if args.info:
        info = initializer.get_storage_info()
        print("\n📊 CFPL Storage Information:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        return
    
    # Initialize storage
    success = initializer.initialize_storage()
    
    if success and args.with_sample_data:
        initializer.create_sample_data()
    
    if success:
        print("\n🎉 CFPL Storage is ready!")
        print("\nNext steps:")
        print("1. Test the viewer with: python cfpl_page_viewer.py render https://example.com/sample")
        print("2. Use the web interface to browse scraped content")
        print("3. Configure retention policies in config/retention.json")

if __name__ == "__main__":
    main()
