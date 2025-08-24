#!/usr/bin/env python3
"""
CFPL Page Viewer System
Advanced viewer for scraped content with full page rendering, image gallery, and network visualization
"""

import json
import os
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
import hashlib
import mimetypes
import base64
from urllib.parse import urljoin, urlparse

class CFPLPageViewer:
    """
    Advanced page viewer for CFPL-stored content
    Provides full page rendering, image extraction, and network visualization
    """
    
    def __init__(self, storage_root: str = "/home/homebrew/scraper/cfpl_storage"):
        self.storage_root = Path(storage_root)
        self.cas_root = self.storage_root / "raw" / "cas" / "sha256"
        self.runs_root = self.storage_root / "raw" / "runs"
        self.catalog_db = self.storage_root / "index" / "catalog.sqlite"
        
    def get_page_content(self, url: str) -> Optional[Dict[str, Any]]:
        """Get full page content including HTML, assets, and metadata"""
        try:
            # Query catalog for this URL
            conn = sqlite3.connect(self.catalog_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT content_sha256, manifest_path 
                FROM captures 
                WHERE url = ?
            """, (url,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return None
                
            content_hash, manifest_path = result
            
            # Load manifest
            manifest_file = self.storage_root / manifest_path
            if not manifest_file.exists():
                return None
                
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
            
            # Get main content
            main_content = self._get_content_by_hash(content_hash)
            
            # Get all assets
            assets = []
            if 'assets' in manifest:
                for asset in manifest['assets']:
                    asset_content = self._get_content_by_hash(asset['sha256'])
                    if asset_content:
                        assets.append({
                            'url': asset['url'],
                            'content_type': asset['content_type'],
                            'size': asset['size'],
                            'content': asset_content,
                            'discovered_via': asset['discovered_via']
                        })
            
            return {
                'url': url,
                'manifest': manifest,
                'main_content': main_content,
                'assets': assets,
                'status': manifest.get('status', 200),
                'content_type': manifest.get('content', {}).get('content_type', 'text/html')
            }
            
        except Exception as e:
            print(f"Error getting page content for {url}: {e}")
            return None
    
    def _get_content_by_hash(self, content_hash: str) -> Optional[bytes]:
        """Retrieve content from CAS by hash"""
        try:
            prefix = content_hash[:2]
            cas_path = self.cas_root / prefix / content_hash
            
            if cas_path.exists():
                with open(cas_path, 'rb') as f:
                    return f.read()
            return None
        except Exception as e:
            print(f"Error retrieving content {content_hash}: {e}")
            return None
    
    def render_page_html(self, url: str, inject_viewer_controls: bool = True) -> Optional[str]:
        """
        Render page as HTML with embedded assets
        Creates a self-contained HTML that works offline
        """
        page_data = self.get_page_content(url)
        if not page_data:
            return None
        
        try:
            main_content = page_data['main_content']
            if isinstance(main_content, bytes):
                # Detect encoding
                encoding = page_data['manifest'].get('content', {}).get('encoding', 'utf-8')
                html_content = main_content.decode(encoding, errors='ignore')
            else:
                html_content = str(main_content)
            
            # Create asset map for embedding
            asset_map = {}
            for asset in page_data['assets']:
                original_url = asset['url']
                content_type = asset['content_type']
                content = asset['content']
                
                if content and content_type:
                    if content_type.startswith('image/'):
                        # Convert image to data URL
                        b64_content = base64.b64encode(content).decode('ascii')
                        data_url = f"data:{content_type};base64,{b64_content}"
                        asset_map[original_url] = data_url
                    elif content_type.startswith('text/css'):
                        # Embed CSS inline
                        css_content = content.decode('utf-8', errors='ignore')
                        asset_map[original_url] = f"data:text/css;charset=utf-8,{css_content}"
                    elif content_type.startswith('application/javascript'):
                        # Embed JS inline
                        js_content = content.decode('utf-8', errors='ignore')
                        asset_map[original_url] = f"data:application/javascript;charset=utf-8,{js_content}"
            
            # Replace asset URLs in HTML
            for original_url, data_url in asset_map.items():
                # Handle various URL formats
                html_content = html_content.replace(f'src="{original_url}"', f'src="{data_url}"')
                html_content = html_content.replace(f"src='{original_url}'", f"src='{data_url}'")
                html_content = html_content.replace(f'href="{original_url}"', f'href="{data_url}"')
                html_content = html_content.replace(f"href='{original_url}'", f"href='{data_url}'")
                
                # Handle relative URLs
                parsed_original = urlparse(original_url)
                if parsed_original.path:
                    relative_path = parsed_original.path
                    html_content = html_content.replace(f'src="{relative_path}"', f'src="{data_url}"')
                    html_content = html_content.replace(f"src='{relative_path}'", f"src='{data_url}'")
                    html_content = html_content.replace(f'href="{relative_path}"', f'href="{data_url}"')
                    html_content = html_content.replace(f"href='{relative_path}'", f"href='{data_url}'")
            
            # Inject viewer controls if requested
            if inject_viewer_controls:
                viewer_controls = self._generate_viewer_controls(page_data)
                # Insert before closing body tag
                html_content = html_content.replace('</body>', f'{viewer_controls}</body>')
            
            return html_content
            
        except Exception as e:
            print(f"Error rendering page {url}: {e}")
            return None
    
    def _generate_viewer_controls(self, page_data: Dict[str, Any]) -> str:
        """Generate viewer control panel HTML"""
        manifest = page_data['manifest']
        
        return f"""
        <div id="cfpl-viewer-controls" style="
            position: fixed; 
            top: 10px; 
            right: 10px; 
            background: rgba(0,0,0,0.9); 
            color: white; 
            padding: 15px; 
            border-radius: 8px; 
            font-family: monospace; 
            font-size: 12px; 
            z-index: 10000; 
            max-width: 300px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.5);
        ">
            <div style="font-weight: bold; margin-bottom: 10px; color: #4CAF50;">📊 CFPL Viewer</div>
            <div><strong>URL:</strong> {page_data['url']}</div>
            <div><strong>Status:</strong> {page_data['status']}</div>
            <div><strong>Size:</strong> {manifest.get('content', {}).get('size', 'Unknown')} bytes</div>
            <div><strong>Assets:</strong> {len(page_data['assets'])}</div>
            <div><strong>Captured:</strong> {manifest.get('fetch_start', 'Unknown')}</div>
            <div style="margin-top: 10px;">
                <button onclick="document.getElementById('cfpl-viewer-controls').style.display='none'" 
                        style="background: #ff4444; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer;">
                    Hide
                </button>
            </div>
        </div>
        """
    
    def get_image_gallery(self, url: str) -> List[Dict[str, Any]]:
        """Extract all images from a page for gallery view"""
        page_data = self.get_page_content(url)
        if not page_data:
            return []
        
        images = []
        for asset in page_data['assets']:
            if asset['content_type'].startswith('image/'):
                # Convert to base64 for display
                b64_content = base64.b64encode(asset['content']).decode('ascii')
                data_url = f"data:{asset['content_type']};base64,{b64_content}"
                
                images.append({
                    'url': asset['url'],
                    'content_type': asset['content_type'],
                    'size': asset['size'],
                    'data_url': data_url,
                    'discovered_via': asset['discovered_via']
                })
        
        return images
    
    def generate_network_diagram(self, run_id: str) -> Dict[str, Any]:
        """
        Generate network diagram showing crawl path and relationships
        Returns data structure suitable for visualization
        """
        try:
            # Find all pages in this run
            conn = sqlite3.connect(self.catalog_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT url, content_sha256, manifest_path 
                FROM captures 
                WHERE manifest_path LIKE ?
            """, (f"%/{run_id}/%",))
            
            results = cursor.fetchall()
            conn.close()
            
            nodes = []
            edges = []
            url_to_id = {}
            
            # Process each page
            for i, (url, content_hash, manifest_path) in enumerate(results):
                # Load manifest for crawl metadata
                manifest_file = self.storage_root / manifest_path
                if manifest_file.exists():
                    with open(manifest_file, 'r') as f:
                        manifest = json.load(f)
                    
                    # Extract crawl metadata if available
                    crawl_meta = {}
                    if 'crawl_metadata' in manifest:
                        crawl_meta = manifest['crawl_metadata']
                    
                    node_id = f"node_{i}"
                    url_to_id[url] = node_id
                    
                    nodes.append({
                        'id': node_id,
                        'url': url,
                        'title': manifest.get('title', url),
                        'status': manifest.get('status', 200),
                        'depth': crawl_meta.get('depth', 0),
                        'discovery_order': crawl_meta.get('discovery_order', i),
                        'processing_time': crawl_meta.get('processing_time', 0),
                        'domain': crawl_meta.get('domain', urlparse(url).netloc),
                        'size': manifest.get('content', {}).get('size', 0)
                    })
            
            # Create edges based on referrer relationships and links
            for i, (url, content_hash, manifest_path) in enumerate(results):
                manifest_file = self.storage_root / manifest_path
                if manifest_file.exists():
                    with open(manifest_file, 'r') as f:
                        manifest = json.load(f)
                    
                    source_id = url_to_id[url]
                    
                    # Look for links in the page content
                    if 'links' in manifest:
                        for link in manifest.get('links', []):
                            target_url = link.get('url', '')
                            if target_url in url_to_id:
                                target_id = url_to_id[target_url]
                                edges.append({
                                    'source': source_id,
                                    'target': target_id,
                                    'type': 'link',
                                    'link_text': link.get('text', '')[:50]
                                })
            
            return {
                'nodes': nodes,
                'edges': edges,
                'metadata': {
                    'run_id': run_id,
                    'total_pages': len(nodes),
                    'total_domains': len(set(node['domain'] for node in nodes)),
                    'crawl_depth': max((node['depth'] for node in nodes), default=0)
                }
            }
            
        except Exception as e:
            print(f"Error generating network diagram for run {run_id}: {e}")
            return {'nodes': [], 'edges': [], 'metadata': {}}
    
    def export_page_bundle(self, url: str, output_dir: str) -> bool:
        """
        Export complete page bundle including HTML, assets, and metadata
        Creates a portable folder with all content
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            page_data = self.get_page_content(url)
            if not page_data:
                return False
            
            # Save main HTML
            html_content = self.render_page_html(url, inject_viewer_controls=False)
            if html_content:
                with open(output_path / "index.html", 'w', encoding='utf-8') as f:
                    f.write(html_content)
            
            # Save assets
            assets_dir = output_path / "assets"
            assets_dir.mkdir(exist_ok=True)
            
            for i, asset in enumerate(page_data['assets']):
                asset_filename = f"asset_{i}_{hashlib.md5(asset['url'].encode()).hexdigest()[:8]}"
                
                # Determine file extension
                content_type = asset['content_type']
                ext = mimetypes.guess_extension(content_type) or '.bin'
                asset_filename += ext
                
                with open(assets_dir / asset_filename, 'wb') as f:
                    f.write(asset['content'])
            
            # Save metadata
            metadata = {
                'url': url,
                'exported_at': page_data['manifest'].get('fetch_start'),
                'manifest': page_data['manifest'],
                'asset_count': len(page_data['assets']),
                'total_size': sum(asset['size'] for asset in page_data['assets'])
            }
            
            with open(output_path / "metadata.json", 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error exporting page bundle for {url}: {e}")
            return False

def main():
    """CLI interface for the page viewer"""
    import argparse
    
    parser = argparse.ArgumentParser(description="CFPL Page Viewer")
    parser.add_argument('--storage-root', default="/home/homebrew/scraper/cfpl_storage",
                       help="CFPL storage root directory")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Render command
    render_parser = subparsers.add_parser('render', help='Render page as HTML')
    render_parser.add_argument('url', help='URL to render')
    render_parser.add_argument('--output', '-o', help='Output HTML file')
    render_parser.add_argument('--no-controls', action='store_true', 
                              help='Don\'t inject viewer controls')
    
    # Images command
    images_parser = subparsers.add_parser('images', help='Extract images from page')
    images_parser.add_argument('url', help='URL to extract images from')
    images_parser.add_argument('--output-dir', '-o', help='Output directory for images')
    
    # Network command
    network_parser = subparsers.add_parser('network', help='Generate network diagram')
    network_parser.add_argument('run_id', help='Run ID to analyze')
    network_parser.add_argument('--output', '-o', help='Output JSON file')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export complete page bundle')
    export_parser.add_argument('url', help='URL to export')
    export_parser.add_argument('output_dir', help='Output directory')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    viewer = CFPLPageViewer(args.storage_root)
    
    if args.command == 'render':
        html = viewer.render_page_html(args.url, not args.no_controls)
        if html:
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(html)
                print(f"✅ Page rendered to {args.output}")
            else:
                print(html)
        else:
            print(f"❌ Failed to render {args.url}")
    
    elif args.command == 'images':
        images = viewer.get_image_gallery(args.url)
        print(f"📸 Found {len(images)} images in {args.url}")
        
        if args.output_dir:
            output_path = Path(args.output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            for i, img in enumerate(images):
                img_filename = f"image_{i}_{hashlib.md5(img['url'].encode()).hexdigest()[:8]}"
                ext = mimetypes.guess_extension(img['content_type']) or '.bin'
                img_filename += ext
                
                # Decode base64 and save
                img_data = base64.b64decode(img['data_url'].split(',')[1])
                with open(output_path / img_filename, 'wb') as f:
                    f.write(img_data)
                
                print(f"  💾 Saved: {img_filename} ({img['size']} bytes)")
        else:
            for img in images:
                print(f"  📄 {img['url']} ({img['content_type']}, {img['size']} bytes)")
    
    elif args.command == 'network':
        diagram = viewer.generate_network_diagram(args.run_id)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(diagram, f, indent=2)
            print(f"✅ Network diagram saved to {args.output}")
        else:
            print(json.dumps(diagram, indent=2))
        
        metadata = diagram['metadata']
        print(f"\n📊 Network Summary:")
        print(f"  Pages: {metadata['total_pages']}")
        print(f"  Domains: {metadata['total_domains']}")
        print(f"  Max Depth: {metadata['crawl_depth']}")
    
    elif args.command == 'export':
        success = viewer.export_page_bundle(args.url, args.output_dir)
        if success:
            print(f"✅ Page bundle exported to {args.output_dir}")
        else:
            print(f"❌ Failed to export {args.url}")

if __name__ == "__main__":
    main()
