#!/usr/bin/env python3
"""
CFPL Command Line Interface
Provides commands for capturing, processing, and inspecting CFPL data
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

# Add the project directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from storage.cas_store import CASStore
from storage.capture_engine import CFPLCaptureEngine, capture_single_url
from storage.config import CFPLConfigManager, get_config
from storage.processors import ProcessingPipeline


async def cmd_capture(args):
    """Capture one or more URLs"""
    config = get_config()
    
    if args.config:
        config_manager = CFPLConfigManager(args.config)
        config = config_manager.load_config()
    
    urls = []
    
    if args.url:
        urls.append(args.url)
    
    if args.url_file:
        with open(args.url_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    urls.append(line)
    
    if not urls:
        print("Error: No URLs specified. Use --url or --url-file", file=sys.stderr)
        return 1
    
    print(f"Capturing {len(urls)} URLs...")
    
    async with CFPLCaptureEngine(config) as engine:
        run_id = engine.start_run(args.run_id)
        print(f"Started run: {run_id}")
        
        results = []
        for i, url in enumerate(urls, 1):
            print(f"[{i}/{len(urls)}] Capturing: {url}")
            
            try:
                result = await engine.capture_url(url, run_id)
                results.append(result)
                
                if result['status'] == 'success':
                    print(f"  ✓ Success: {result['content_hash'][:16]}... "
                          f"({result['assets_captured']} assets, {result['media_captured']} media)")
                else:
                    print(f"  ✗ Failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"  ✗ Exception: {str(e)}")
                results.append({"status": "error", "url": url, "error": str(e)})
    
    # Summary
    successful = sum(1 for r in results if r.get('status') == 'success')
    print(f"\nCapture complete: {successful}/{len(urls)} successful")
    
    if args.auto_process:
        print("\nStarting automatic processing...")
        pipeline = ProcessingPipeline(config)
        await pipeline.process_run(run_id)
        print("Processing complete")
    
    return 0


async def cmd_process(args):
    """Process captured data"""
    config = get_config()
    
    if args.config:
        config_manager = CFPLConfigManager(args.config)
        config = config_manager.load_config()
    
    pipeline = ProcessingPipeline(config)
    
    if args.run_id:
        result = await pipeline.process_run(args.run_id)
        print(json.dumps(result, indent=2))
    elif args.manifest:
        result = await pipeline.process_manifest(args.manifest, args.run_id or "manual")
        print(json.dumps(result, indent=2))
    else:
        print("Error: Must specify --run-id or --manifest", file=sys.stderr)
        return 1
    
    return 0


def cmd_inspect(args):
    """Inspect stored data"""
    config = get_config()
    cas_store = CASStore(config.storage.root)
    
    if args.stats:
        stats = cas_store.get_storage_stats()
        print(json.dumps(stats, indent=2))
        
    elif args.list_captures:
        captures = cas_store.query_captures(limit=args.limit or 50)
        for capture in captures:
            print(f"{capture['timestamp']} {capture['status']} {capture['url']}")
            
    elif args.search:
        captures = cas_store.query_captures(url=args.search, limit=args.limit or 10)
        print(json.dumps(captures, indent=2))
        
    elif args.content_hash:
        try:
            content = cas_store.retrieve_content(args.content_hash)
            if args.output:
                with open(args.output, 'wb') as f:
                    f.write(content)
                print(f"Content saved to {args.output}")
            else:
                # Print content info
                print(f"Content size: {len(content)} bytes")
                print(f"Content hash: {args.content_hash}")
                if len(content) < 1024 and content.startswith(b'<'):
                    print("Preview:")
                    print(content.decode('utf-8', errors='ignore')[:500])
        except FileNotFoundError:
            print(f"Content not found: {args.content_hash}", file=sys.stderr)
            return 1
            
    return 0


def cmd_config(args):
    """Manage configuration"""
    if args.init:
        config_manager = CFPLConfigManager(args.config or './cfpl_config.json')
        config = config_manager.load_config()
        print(f"Configuration initialized: {config_manager.config_path}")
        
    elif args.show:
        config = get_config()
        config_dict = {
            'capture': config.capture.__dict__,
            'storage': config.storage.__dict__,
            'limits': config.limits.__dict__,
            'privacy': config.privacy.__dict__,
            'retention': config.retention.__dict__,
            'processing': config.processing.__dict__
        }
        print(json.dumps(config_dict, indent=2))
        
    elif args.set:
        # Parse key=value pairs
        updates = {}
        for setting in args.set:
            if '=' not in setting:
                print(f"Invalid setting format: {setting}", file=sys.stderr)
                return 1
            
            key, value = setting.split('=', 1)
            
            # Parse nested keys (e.g., storage.root)
            keys = key.split('.')
            current = updates
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            
            # Try to parse value as JSON, fallback to string
            try:
                current[keys[-1]] = json.loads(value)
            except json.JSONDecodeError:
                current[keys[-1]] = value
        
        config_manager = CFPLConfigManager(args.config)
        config_manager.update_config(updates)
        print("Configuration updated")
        
    return 0


def cmd_cleanup(args):
    """Clean up old data"""
    config = get_config()
    cas_store = CASStore(config.storage.root)
    
    retention_days = args.days or config.retention.raw_years * 365
    
    if args.dry_run:
        print(f"DRY RUN: Would clean up data older than {retention_days} days")
        # TODO: Implement dry run logic
        return 0
    
    if not args.confirm:
        response = input(f"Delete data older than {retention_days} days? [y/N]: ")
        if response.lower() != 'y':
            print("Cancelled")
            return 0
    
    result = cas_store.cleanup_old_content(retention_days)
    print(f"Cleanup complete:")
    print(f"  Deleted manifests: {result['deleted_manifests']}")
    print(f"  Deleted content objects: {result['deleted_content_objects']}")
    print(f"  Retention cutoff: {result['retention_cutoff']}")
    
    return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="CFPL (Capture-First, Process-Later) Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Capture a single URL
  cfpl capture --url https://example.com
  
  # Capture multiple URLs from file
  cfpl capture --url-file urls.txt --auto-process
  
  # Process a specific run
  cfpl process --run-id cfpl_20250818_123456_abc123
  
  # Show storage statistics
  cfpl inspect --stats
  
  # Initialize configuration
  cfpl config --init
  
  # Clean up old data
  cfpl cleanup --days 30 --confirm
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Capture command
    capture_parser = subparsers.add_parser('capture', help='Capture URLs')
    capture_parser.add_argument('--url', help='Single URL to capture')
    capture_parser.add_argument('--url-file', help='File containing URLs to capture (one per line)')
    capture_parser.add_argument('--run-id', help='Custom run ID (auto-generated if not specified)')
    capture_parser.add_argument('--config', help='Configuration file path')
    capture_parser.add_argument('--auto-process', action='store_true', help='Automatically process after capture')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process captured data')
    process_parser.add_argument('--run-id', help='Process all manifests in a run')
    process_parser.add_argument('--manifest', help='Process a specific manifest file')
    process_parser.add_argument('--config', help='Configuration file path')
    
    # Inspect command
    inspect_parser = subparsers.add_parser('inspect', help='Inspect stored data')
    inspect_parser.add_argument('--stats', action='store_true', help='Show storage statistics')
    inspect_parser.add_argument('--list-captures', action='store_true', help='List recent captures')
    inspect_parser.add_argument('--search', help='Search captures by URL')
    inspect_parser.add_argument('--content-hash', help='Retrieve content by hash')
    inspect_parser.add_argument('--output', help='Output file for content retrieval')
    inspect_parser.add_argument('--limit', type=int, help='Limit number of results')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_parser.add_argument('--init', action='store_true', help='Initialize default configuration')
    config_parser.add_argument('--show', action='store_true', help='Show current configuration')
    config_parser.add_argument('--set', nargs='+', help='Set configuration values (key=value)')
    config_parser.add_argument('--config', help='Configuration file path')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old data')
    cleanup_parser.add_argument('--days', type=int, help='Delete data older than N days')
    cleanup_parser.add_argument('--dry-run', action='store_true', help='Show what would be deleted')
    cleanup_parser.add_argument('--confirm', action='store_true', help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    try:
        if args.command == 'capture':
            return asyncio.run(cmd_capture(args))
        elif args.command == 'process':
            return asyncio.run(cmd_process(args))
        elif args.command == 'inspect':
            return cmd_inspect(args)
        elif args.command == 'config':
            return cmd_config(args)
        elif args.command == 'cleanup':
            return cmd_cleanup(args)
        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            return 1
            
    except KeyboardInterrupt:
        print("\nCancelled by user")
        return 1
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
