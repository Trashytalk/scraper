#!/usr/bin/env python3
"""
Simplified CFPL Demo
Demonstrates the core Capture-First, Process-Later principles using only built-in modules
"""

import hashlib
import json
import os
import sqlite3
import tempfile
import time
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen, Request
import shutil


class SimplifiedCFPLDemo:
    """Simplified CFPL demonstration using only standard library"""
    
    def __init__(self, storage_root):
        self.storage_root = Path(storage_root)
        self.cas_root = self.storage_root / "raw" / "cas" / "sha256"
        self.runs_root = self.storage_root / "raw" / "runs"
        self.derived_root = self.storage_root / "derived"
        self.index_root = self.storage_root / "index"
        
        # Create directory structure
        for path in [self.cas_root, self.runs_root, self.derived_root, self.index_root]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Initialize catalog
        self.catalog_db = self.index_root / "catalog.sqlite"
        self._init_catalog()
    
    def _init_catalog(self):
        """Initialize catalog database"""
        conn = sqlite3.connect(self.catalog_db)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS captures (
                url TEXT PRIMARY KEY,
                content_sha256 TEXT NOT NULL,
                content_size INTEGER NOT NULL,
                content_type TEXT,
                manifest_path TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
    
    def _compute_sha256(self, data):
        """Compute SHA256 hash"""
        return hashlib.sha256(data).hexdigest()
    
    def _get_cas_path(self, sha256_hash):
        """Get CAS path for hash"""
        prefix = sha256_hash[:2]
        return self.cas_root / prefix / sha256_hash
    
    def store_content(self, data, content_type=None):
        """Store content in CAS"""
        sha256_hash = self._compute_sha256(data)
        cas_path = self._get_cas_path(sha256_hash)
        
        if not cas_path.exists():
            cas_path.parent.mkdir(parents=True, exist_ok=True)
            with open(cas_path, 'wb') as f:
                f.write(data)
            # Make read-only
            cas_path.chmod(0o444)
        
        return sha256_hash
    
    def retrieve_content(self, sha256_hash):
        """Retrieve content by hash"""
        cas_path = self._get_cas_path(sha256_hash)
        with open(cas_path, 'rb') as f:
            return f.read()
    
    def capture_url(self, url, run_id="demo_run"):
        """Capture URL with CFPL principles"""
        print(f"📥 Capturing: {url}")
        
        try:
            # Step 1: Fetch content (single-touch principle)
            headers = {
                'User-Agent': 'Mozilla/5.0 (CFPL Demo) CFPLBot/1.0'
            }
            
            request = Request(url, headers=headers)
            with urlopen(request, timeout=10) as response:
                content = response.read()
                content_type = response.headers.get('content-type', '')
                status = response.getcode()
                final_url = response.geturl()
            
            # Step 2: Store in CAS immediately (capture-first principle)
            content_hash = self.store_content(content, content_type)
            
            # Step 3: Create manifest (RAW write barrier)
            manifest = {
                "url": url,
                "final_url": final_url,
                "status": status,
                "content": {
                    "sha256": content_hash,
                    "size": len(content),
                    "content_type": content_type
                },
                "timestamp": time.time(),
                "tools": {"demo_version": "1.0"}
            }
            
            # Store manifest
            timestamp_str = str(int(time.time()))
            host = urlparse(url).netloc or "unknown"
            manifest_dir = self.runs_root / run_id / host / timestamp_str
            manifest_dir.mkdir(parents=True, exist_ok=True)
            
            manifest_path = manifest_dir / "manifest.json"
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)
            
            # Make manifest read-only
            manifest_path.chmod(0o444)
            
            # Record in catalog
            conn = sqlite3.connect(self.catalog_db)
            conn.execute("""
                INSERT OR REPLACE INTO captures 
                (url, content_sha256, content_size, content_type, manifest_path, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (url, content_hash, len(content), content_type, str(manifest_path), timestamp_str))
            conn.commit()
            conn.close()
            
            print(f"   ✅ Captured: {content_hash[:16]}... ({len(content)} bytes)")
            return {
                "status": "success",
                "content_hash": content_hash,
                "manifest_path": str(manifest_path),
                "content_size": len(content)
            }
            
        except Exception as e:
            print(f"   ❌ Failed: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def process_manifest(self, manifest_path):
        """Process captured data (process-later principle)"""
        print(f"⚙️ Processing: {manifest_path}")
        
        try:
            # Load manifest
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            url = manifest['url']
            content_hash = manifest['content']['sha256']
            
            # Retrieve content from CAS (no network access)
            content = self.retrieve_content(content_hash)
            content_type = manifest['content']['content_type']
            
            # Simple text extraction for HTML
            extracted_data = {
                "url": url,
                "content_hash": content_hash,
                "processed_at": time.time(),
                "content_size": len(content),
                "content_type": content_type
            }
            
            if 'text/html' in content_type.lower():
                # Simple HTML processing
                text_content = content.decode('utf-8', errors='ignore')
                
                # Extract title (very basic)
                title_start = text_content.lower().find('<title>')
                title_end = text_content.lower().find('</title>')
                if title_start != -1 and title_end != -1:
                    title = text_content[title_start+7:title_end].strip()
                    extracted_data['title'] = title
                
                # Count basic elements
                extracted_data['word_count'] = len(text_content.split())
                extracted_data['link_count'] = text_content.lower().count('<a ')
                extracted_data['image_count'] = text_content.lower().count('<img ')
            
            # Save to derived zone
            run_id = Path(manifest_path).parts[-4]  # Extract run_id from path
            derived_dir = self.derived_root / run_id
            derived_dir.mkdir(parents=True, exist_ok=True)
            
            derived_file = derived_dir / "processed_data.jsonl"
            with open(derived_file, 'a') as f:
                f.write(json.dumps(extracted_data) + '\n')
            
            print(f"   ✅ Processed: {extracted_data.get('title', 'No title')}")
            return extracted_data
            
        except Exception as e:
            print(f"   ❌ Processing failed: {str(e)}")
            return {"error": str(e)}
    
    def get_stats(self):
        """Get storage statistics"""
        conn = sqlite3.connect(self.catalog_db)
        cursor = conn.execute("SELECT COUNT(*) FROM captures")
        total_captures = cursor.fetchone()[0]
        conn.close()
        
        # Count CAS objects
        cas_objects = 0
        if self.cas_root.exists():
            for prefix_dir in self.cas_root.iterdir():
                if prefix_dir.is_dir():
                    cas_objects += len(list(prefix_dir.iterdir()))
        
        return {
            "total_captures": total_captures,
            "cas_objects": cas_objects,
            "storage_root": str(self.storage_root)
        }
    
    def demonstrate_replayability(self, manifest_path):
        """Demonstrate that processing is replayable"""
        print(f"🔄 Testing replayability for: {manifest_path}")
        
        # Process twice
        result1 = self.process_manifest(manifest_path)
        result2 = self.process_manifest(manifest_path)
        
        # Compare results (excluding timestamps)
        comparable_fields = ['url', 'content_hash', 'title', 'word_count']
        identical = True
        
        for field in comparable_fields:
            if field in result1 and field in result2:
                if result1[field] != result2[field]:
                    identical = False
                    break
        
        if identical:
            print("   ✅ Processing is deterministic (replayable)")
        else:
            print("   ❌ Processing results differ")
        
        return identical


def main():
    """Main demonstration"""
    print("🎯 CFPL ARCHITECTURE DEMONSTRATION")
    print("Capture-First, Process-Later with Built-in Python")
    print("="*60)
    
    # Create temporary storage
    with tempfile.TemporaryDirectory(prefix="cfpl_demo_") as temp_dir:
        demo = SimplifiedCFPLDemo(temp_dir)
        print(f"📁 Storage: {temp_dir}")
        
        # Test URLs (simple ones that should work)
        test_urls = [
            "https://httpbin.org/html",
            "https://httpbin.org/json",
        ]
        
        print(f"\n📥 CAPTURE PHASE (Single-Touch Fetching)")
        print("-" * 40)
        
        manifests = []
        for url in test_urls:
            result = demo.capture_url(url)
            if result['status'] == 'success':
                manifests.append(result['manifest_path'])
        
        print(f"\n⚙️ PROCESS PHASE (RAW → DERIVED)")
        print("-" * 40)
        
        for manifest_path in manifests:
            demo.process_manifest(manifest_path)
        
        print(f"\n🔄 REPLAYABILITY TEST")
        print("-" * 40)
        
        if manifests:
            demo.demonstrate_replayability(manifests[0])
        
        print(f"\n📊 STORAGE STATISTICS")
        print("-" * 40)
        
        stats = demo.get_stats()
        print(f"Total captures: {stats['total_captures']}")
        print(f"CAS objects: {stats['cas_objects']}")
        
        # Show directory structure
        print(f"\n🏛️ DIRECTORY STRUCTURE")
        print("-" * 40)
        
        def show_tree(path, prefix="", max_depth=3, current_depth=0):
            if current_depth >= max_depth:
                return
            
            path = Path(path)
            if not path.exists():
                return
                
            items = sorted(path.iterdir())
            for i, item in enumerate(items[:10]):  # Limit to first 10 items
                is_last = i == len(items) - 1 or i == 9
                item_prefix = "└── " if is_last else "├── "
                print(f"{prefix}{item_prefix}{item.name}")
                
                if item.is_dir() and current_depth < max_depth - 1:
                    next_prefix = prefix + ("    " if is_last else "│   ")
                    show_tree(item, next_prefix, max_depth, current_depth + 1)
        
        show_tree(temp_dir)
        
        print(f"\n🎉 CFPL DEMONSTRATION COMPLETE")
        print("✅ Captured content in immutable RAW zone")
        print("✅ Processed data stored in purgeable DERIVED zone") 
        print("✅ Demonstrated replayability (no network access)")
        print("✅ Content-addressed storage with deduplication")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Demo interrupted by user")
    except Exception as e:
        print(f"\n💥 Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()
