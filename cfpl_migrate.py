#!/usr/bin/env python3
"""
CFPL Migration Script
Migrate existing scraping data to CFPL architecture and provide transition guidance
"""

import json
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class CFPLMigrationTool:
    """Tool to migrate existing scraping data to CFPL architecture"""
    
    def __init__(self, storage_root: str):
        self.storage_root = Path(storage_root)
        self.legacy_db_paths = [
            "data.db",
            "analytics.db", 
            "data/scraper.db",
            "./scraper.db"
        ]
    
    def scan_legacy_data(self) -> Dict[str, Any]:
        """Scan for existing scraping data"""
        print("🔍 Scanning for legacy scraping data...")
        
        legacy_data = {
            "databases": [],
            "cache_files": [],
            "log_files": [],
            "config_files": [],
            "total_size": 0
        }
        
        # Check for SQLite databases
        for db_path in self.legacy_db_paths:
            full_path = Path(db_path)
            if full_path.exists():
                size = full_path.stat().st_size
                legacy_data["databases"].append({
                    "path": str(full_path),
                    "size": size,
                    "tables": self._get_db_tables(full_path)
                })
                legacy_data["total_size"] += size
                print(f"   📄 Found database: {full_path} ({size:,} bytes)")
        
        # Check for cache directories
        cache_dirs = ["cache", "http_cache", "__pycache__"]
        for cache_dir in cache_dirs:
            cache_path = Path(cache_dir)
            if cache_path.exists() and cache_path.is_dir():
                size = sum(f.stat().st_size for f in cache_path.rglob('*') if f.is_file())
                if size > 0:
                    legacy_data["cache_files"].append({
                        "path": str(cache_path),
                        "size": size
                    })
                    legacy_data["total_size"] += size
                    print(f"   📁 Found cache: {cache_path} ({size:,} bytes)")
        
        # Check for log files
        log_patterns = ["*.log", "logs/*", "*.out"]
        for pattern in log_patterns:
            for log_file in Path(".").glob(pattern):
                if log_file.is_file():
                    size = log_file.stat().st_size
                    legacy_data["log_files"].append({
                        "path": str(log_file),
                        "size": size
                    })
                    legacy_data["total_size"] += size
                    print(f"   📝 Found log: {log_file} ({size:,} bytes)")
        
        return legacy_data
    
    def _get_db_tables(self, db_path: Path) -> List[str]:
        """Get table names from SQLite database"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            return tables
        except Exception as e:
            print(f"   ⚠️ Could not read {db_path}: {e}")
            return []
    
    def create_cfpl_structure(self):
        """Create CFPL directory structure"""
        print("\n🏗️ Creating CFPL directory structure...")
        
        # CFPL directories
        cfpl_dirs = [
            self.storage_root / "raw" / "cas" / "sha256",
            self.storage_root / "raw" / "runs",
            self.storage_root / "derived",
            self.storage_root / "index",
            self.storage_root / "config"
        ]
        
        for directory in cfpl_dirs:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ Created: {directory}")
        
        # Create initial catalog database
        catalog_db = self.storage_root / "index" / "catalog.sqlite"
        if not catalog_db.exists():
            conn = sqlite3.connect(catalog_db)
            conn.execute("""
                CREATE TABLE captures (
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
                    migrated_from TEXT,
                    created_at TEXT NOT NULL,
                    UNIQUE(url, timestamp, run_id)
                )
            """)
            conn.execute("CREATE INDEX idx_captures_url ON captures(url)")
            conn.execute("CREATE INDEX idx_captures_sha256 ON captures(content_sha256)")
            conn.commit()
            conn.close()
            print(f"   ✅ Created catalog: {catalog_db}")
    
    def migrate_legacy_database(self, db_path: str) -> Dict[str, Any]:
        """Migrate data from legacy database"""
        print(f"\n📦 Migrating legacy database: {db_path}")
        
        db_file = Path(db_path)
        if not db_file.exists():
            return {"error": f"Database not found: {db_path}"}
        
        migration_stats = {
            "records_processed": 0,
            "records_migrated": 0,
            "errors": [],
            "run_id": f"migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        
        try:
            conn = sqlite3.connect(db_file)
            
            # Try to find crawl data tables
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            print(f"   📊 Found tables: {', '.join(tables)}")
            
            # Look for common table patterns
            data_tables = [t for t in tables if any(pattern in t.lower() 
                          for pattern in ['crawl', 'scrape', 'page', 'url', 'cache'])]
            
            if not data_tables:
                print("   ⚠️ No recognizable data tables found")
                return migration_stats
            
            for table in data_tables:
                print(f"   🔄 Processing table: {table}")
                
                try:
                    # Get table schema
                    cursor = conn.execute(f"PRAGMA table_info({table})")
                    columns = [row[1] for row in cursor.fetchall()]
                    
                    # Look for URL and content columns
                    url_col = None
                    content_col = None
                    timestamp_col = None
                    
                    for col in columns:
                        col_lower = col.lower()
                        if 'url' in col_lower and not url_col:
                            url_col = col
                        elif any(term in col_lower for term in ['content', 'html', 'data']) and not content_col:
                            content_col = col
                        elif any(term in col_lower for term in ['time', 'date', 'created']) and not timestamp_col:
                            timestamp_col = col
                    
                    if not url_col:
                        print(f"     ⚠️ No URL column found in {table}")
                        continue
                    
                    # Query data
                    query = f"SELECT * FROM {table}"
                    cursor = conn.execute(query)
                    rows = cursor.fetchall()
                    
                    print(f"     📄 Found {len(rows)} records")
                    
                    for row in rows:
                        migration_stats["records_processed"] += 1
                        
                        # Extract data
                        row_dict = dict(zip(columns, row))
                        url = row_dict.get(url_col, '')
                        
                        if not url or not url.startswith('http'):
                            continue
                        
                        # Create pseudo-manifest for legacy data
                        manifest = {
                            "url": url,
                            "final_url": url,
                            "status": 200,  # Assume success for legacy data
                            "timestamp": row_dict.get(timestamp_col, datetime.now().isoformat()),
                            "legacy_migration": {
                                "source_table": table,
                                "source_database": db_path,
                                "migrated_at": datetime.now().isoformat(),
                                "original_data": row_dict
                            },
                            "content": {
                                "sha256": "legacy_placeholder",
                                "size": len(str(row_dict.get(content_col, ''))),
                                "content_type": "text/html"
                            }
                        }
                        
                        # Create manifest file
                        run_dir = (self.storage_root / "raw" / "runs" / 
                                 migration_stats["run_id"] / "legacy" / 
                                 str(migration_stats["records_migrated"]))
                        run_dir.mkdir(parents=True, exist_ok=True)
                        
                        manifest_path = run_dir / "manifest.json"
                        with open(manifest_path, 'w') as f:
                            json.dump(manifest, f, indent=2)
                        
                        migration_stats["records_migrated"] += 1
                        
                        if migration_stats["records_migrated"] % 10 == 0:
                            print(f"     📈 Migrated {migration_stats['records_migrated']} records...")
                
                except Exception as e:
                    error_msg = f"Error processing table {table}: {str(e)}"
                    migration_stats["errors"].append(error_msg)
                    print(f"     ❌ {error_msg}")
            
            conn.close()
            
        except Exception as e:
            error_msg = f"Error reading database {db_path}: {str(e)}"
            migration_stats["errors"].append(error_msg)
            print(f"   ❌ {error_msg}")
        
        return migration_stats
    
    def create_migration_summary(self, legacy_data: Dict, migration_results: List[Dict]) -> str:
        """Create migration summary report"""
        summary_path = self.storage_root / "MIGRATION_SUMMARY.md"
        
        with open(summary_path, 'w') as f:
            f.write("# CFPL Migration Summary\n\n")
            f.write(f"Migration completed: {datetime.now().isoformat()}\n\n")
            
            f.write("## Legacy Data Scanned\n\n")
            f.write(f"- **Total size**: {legacy_data['total_size']:,} bytes\n")
            f.write(f"- **Databases**: {len(legacy_data['databases'])}\n")
            f.write(f"- **Cache files**: {len(legacy_data['cache_files'])}\n")
            f.write(f"- **Log files**: {len(legacy_data['log_files'])}\n\n")
            
            if legacy_data['databases']:
                f.write("### Databases Found\n\n")
                for db in legacy_data['databases']:
                    f.write(f"- `{db['path']}` ({db['size']:,} bytes)\n")
                    f.write(f"  - Tables: {', '.join(db['tables'])}\n")
                f.write("\n")
            
            f.write("## Migration Results\n\n")
            total_migrated = sum(r.get('records_migrated', 0) for r in migration_results)
            total_processed = sum(r.get('records_processed', 0) for r in migration_results)
            
            f.write(f"- **Records processed**: {total_processed:,}\n")
            f.write(f"- **Records migrated**: {total_migrated:,}\n")
            f.write(f"- **Success rate**: {(total_migrated/max(total_processed,1))*100:.1f}%\n\n")
            
            f.write("## CFPL Structure Created\n\n")
            f.write("```\n")
            f.write(f"{self.storage_root}/\n")
            f.write("├── raw/          # Immutable capture zone\n")
            f.write("│   ├── cas/       # Content-addressed storage\n")
            f.write("│   └── runs/      # Organized by run/host/timestamp\n")
            f.write("├── derived/      # Purgeable processed data\n")
            f.write("├── index/        # Fast lookup databases\n")
            f.write("└── config/       # Configuration files\n")
            f.write("```\n\n")
            
            f.write("## Next Steps\n\n")
            f.write("1. **Update code** to use CFPL scraping engine:\n")
            f.write("   ```python\n")
            f.write("   from storage import CFPLScrapingEngine\n")
            f.write("   \n")
            f.write("   async with CFPLScrapingEngine() as scraper:\n")
            f.write("       result = await scraper.scrape_url(url)\n")
            f.write("   ```\n\n")
            
            f.write("2. **Configure CFPL settings**:\n")
            f.write("   - Run `python3 cfpl_cli.py config --init`\n")
            f.write("   - Edit `cfpl_config.json` as needed\n\n")
            
            f.write("3. **Test the new system**:\n")
            f.write("   - Run `python3 test_crawl_fix.py` to validate\n")
            f.write("   - Use `python3 cfpl_cli.py` for command-line operations\n\n")
            
            f.write("4. **Gradual transition**:\n")
            f.write("   - CFPL is backward-compatible with existing `scrape_url()` interface\n")
            f.write("   - Gradually migrate scripts to use CFPL features\n")
            f.write("   - Old database can remain as reference\n\n")
        
        return str(summary_path)
    
    def run_migration(self) -> bool:
        """Run complete migration process"""
        print("🚀 CFPL MIGRATION TOOL")
        print("="*50)
        
        # Scan legacy data
        legacy_data = self.scan_legacy_data()
        
        if legacy_data["total_size"] == 0:
            print("ℹ️  No legacy data found. Creating fresh CFPL structure...")
        
        # Create CFPL structure
        self.create_cfpl_structure()
        
        # Migrate databases
        migration_results = []
        for db_info in legacy_data["databases"]:
            result = self.migrate_legacy_database(db_info["path"])
            migration_results.append(result)
        
        # Create summary
        summary_path = self.create_migration_summary(legacy_data, migration_results)
        
        print(f"\n✅ Migration complete!")
        print(f"📄 Summary: {summary_path}")
        print(f"🏗️  CFPL structure: {self.storage_root}")
        
        return True


def main():
    """Main migration execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate to CFPL architecture")
    parser.add_argument("--storage-root", default="./cfpl_storage", 
                       help="Root directory for CFPL storage")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be migrated without making changes")
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        print("="*50)
        
        # Just scan and report
        migration_tool = CFPLMigrationTool(args.storage_root)
        legacy_data = migration_tool.scan_legacy_data()
        
        print(f"\nWould create CFPL structure in: {args.storage_root}")
        print(f"Would migrate {len(legacy_data['databases'])} databases")
        print("Run without --dry-run to perform migration")
        
    else:
        migration_tool = CFPLMigrationTool(args.storage_root)
        success = migration_tool.run_migration()
        
        if success:
            print("\n🎉 Ready to use CFPL!")
            print("Run 'python3 cfpl_demo.py' to see it in action")
        
        return 0 if success else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Migration failed: {str(e)}")
        sys.exit(1)
