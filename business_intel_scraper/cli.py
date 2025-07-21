"""Simple command line client for the BI scraper API."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import httpx

# Import Phase 2 CLI functionality
try:
    from .backend.cli.phase2_cli import setup_dom_change_parser, setup_spider_update_parser
    from .backend.cli.phase2_cli import check_dom_changes_command, list_dom_changes_command
    from .backend.cli.phase2_cli import analyze_page_command, generate_dom_report_command
    from .backend.cli.phase2_cli import check_spider_updates_command, spider_update_status_command
    from .backend.cli.phase2_cli import spider_update_history_command
    PHASE2_AVAILABLE = True
except ImportError:
    PHASE2_AVAILABLE = False

# Import Phase 3 CLI functionality
try:
    from .backend.cli.phase3_commands import phase3_cli
    PHASE3_AVAILABLE = True
except ImportError:
    PHASE3_AVAILABLE = False


DEFAULT_URL = os.getenv("BI_SCRAPER_URL", "http://localhost:8000")
DEFAULT_TOKEN = os.getenv("BI_SCRAPER_TOKEN", "")


def _headers(token: str) -> dict[str, str]:
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def start_scrape(url: str, token: str) -> None:
    resp = httpx.post(f"{url}/scrape", headers=_headers(token))
    resp.raise_for_status()
    print(resp.json()["task_id"])


def check_status(url: str, token: str, task_id: str) -> None:
    resp = httpx.get(f"{url}/tasks/{task_id}", headers=_headers(token))
    resp.raise_for_status()
    print(resp.json()["status"])


def download_data(url: str, token: str, output: str | None) -> None:
    resp = httpx.get(f"{url}/data", headers=_headers(token))
    resp.raise_for_status()
    data = resp.json()
    if output:
        Path(output).write_text(json.dumps(data, indent=2))
    else:
        print(json.dumps(data, indent=2))


def export_data(
    url: str,
    token: str,
    fmt: str,
    output: str | None,
    bucket: str | None,
    key: str | None,
) -> None:
    params = {"format": fmt}
    if bucket:
        params["bucket"] = bucket
    if key:
        params["key"] = key
    resp = httpx.get(f"{url}/export", params=params, headers=_headers(token))
    resp.raise_for_status()
    if fmt == "s3":
        print(resp.json().get("location", ""))
    else:
        text = resp.text
        if output:
            Path(output).write_text(text)
        else:
            print(text)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Business Intelligence Scraper - Complete Automation Suite"
    )
    parser.add_argument("--url", default=DEFAULT_URL, help="API base URL")
    parser.add_argument("--token", default=DEFAULT_TOKEN, help="Bearer token")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # Legacy API commands
    api_group = sub.add_parser("api", help="API operations")
    api_sub = api_group.add_subparsers(dest="api_cmd", required=True)
    
    api_sub.add_parser("scrape", help="Launch a scraping job")

    stat = api_sub.add_parser("status", help="Check job status")
    stat.add_argument("task_id")

    dl = api_sub.add_parser("download", help="Download scraped data")
    dl.add_argument("-o", "--output")

    exp = api_sub.add_parser("export", help="Export data in various formats")
    exp.add_argument("--format", choices=["csv", "jsonl", "s3"], default="jsonl")
    exp.add_argument("--bucket")
    exp.add_argument("--key")
    exp.add_argument("-o", "--output")

    # Phase 2 commands (if available)
    if PHASE2_AVAILABLE:
        setup_dom_change_parser(sub)
        setup_spider_update_parser(sub)
        
        # Add demo command
        demo_parser = sub.add_parser("demo", help="Run Phase 2/3 demonstrations")
        demo_parser.add_argument("--phase", choices=['2', '3', 'all'], default='all', help="Demo phase to run")
        demo_parser.add_argument("--component", 
                               choices=['dom', 'changes', 'updates', 'scheduling', 'integration', 
                                      'ml-analysis', 'quality', 'patterns', 'discovery', 'all'],
                               default='all',
                               help="Demo component to run")

    # Phase 3 commands (if available)
    if PHASE3_AVAILABLE:
        phase3_parser = sub.add_parser("phase3", help="Phase 3: Advanced ML-Powered Discovery")
        phase3_subparsers = phase3_parser.add_subparsers(dest="phase3_cmd", required=True)
        
        # Content analysis
        analyze_parser = phase3_subparsers.add_parser("analyze-content", help="Analyze content using ML")
        analyze_parser.add_argument("url", help="URL to analyze")
        analyze_parser.add_argument("--html-file", type=str, help="HTML file to analyze instead of fetching URL")
        analyze_parser.add_argument("--output", "-o", type=str, help="Output file for analysis results")
        analyze_parser.add_argument("--detailed", action="store_true", help="Show detailed feature analysis")
        
        # Quality assessment
        quality_parser = phase3_subparsers.add_parser("assess-quality", help="Assess data quality using ML")
        quality_parser.add_argument("data_file", help="Data file to assess")
        quality_parser.add_argument("--source-url", help="Source URL of the data")
        quality_parser.add_argument("--format", choices=["json", "csv", "raw"], default="json", help="Data format")
        quality_parser.add_argument("--output", "-o", type=str, help="Output file for quality report")
        quality_parser.add_argument("--detailed", action="store_true", help="Show detailed quality metrics")
        
        # Pattern learning
        learn_parser = phase3_subparsers.add_parser("learn-patterns", help="Learn patterns from spider execution")
        learn_parser.add_argument("session_file", help="Session data file")
        learn_parser.add_argument("--output", "-o", type=str, help="Output file for learned patterns")
        
        # Source discovery
        discover_parser = phase3_subparsers.add_parser("discover-sources", help="Discover related sources using ML")
        discover_parser.add_argument("seed_url", help="Seed URL for discovery")
        discover_parser.add_argument("--max-sources", type=int, default=10, help="Maximum number of sources to discover")
        discover_parser.add_argument("--output", "-o", type=str, help="Output file for discovered sources")
        
        # Selector optimization
        optimize_parser = phase3_subparsers.add_parser("optimize-selectors", help="Optimize extraction selectors")
        optimize_parser.add_argument("url", help="URL to optimize selectors for")
        optimize_parser.add_argument("selectors", nargs="+", help="Selectors to optimize")
        optimize_parser.add_argument("--output", "-o", type=str, help="Output file for optimization results")
        
        # Learning cycle
        cycle_parser = phase3_subparsers.add_parser("run-learning-cycle", help="Run adaptive learning cycle")
        
        # Insights report
        insights_parser = phase3_subparsers.add_parser("generate-insights", help="Generate ML insights report")
        insights_parser.add_argument("--days", type=int, default=30, help="Number of days to include in report")
        insights_parser.add_argument("--output", "-o", type=str, help="Output file for insights report")
        
        # System status
        status_parser = phase3_subparsers.add_parser("status", help="Show Phase 3 system status")

    args = parser.parse_args()

    # Route API commands
    if args.cmd == "api":
        if args.api_cmd == "scrape":
            start_scrape(args.url, args.token)
        elif args.api_cmd == "status":
            check_status(args.url, args.token, args.task_id)
        elif args.api_cmd == "download":
            download_data(args.url, args.token, args.output)
        elif args.api_cmd == "export":
            export_data(
                args.url,
                args.token,
                args.format,
                args.output,
                args.bucket,
                args.key,
            )
    
    # Route Phase 2 commands
    elif PHASE2_AVAILABLE and hasattr(args, 'dom_command') and args.dom_command:
        import asyncio
        
        if args.dom_command == 'check':
            success = asyncio.run(check_dom_changes_command(args))
        elif args.dom_command == 'list':
            success = list_dom_changes_command(args)
        elif args.dom_command == 'analyze':
            success = asyncio.run(analyze_page_command(args))
        elif args.dom_command == 'report':
            success = generate_dom_report_command(args)
        else:
            success = False
            
        sys.exit(0 if success else 1)
    
    elif PHASE2_AVAILABLE and hasattr(args, 'update_command') and args.update_command:
        import asyncio
        
        if args.update_command == 'check':
            success = asyncio.run(check_spider_updates_command(args))
        elif args.update_command == 'status':
            success = spider_update_status_command(args)
        elif args.update_command == 'history':
            success = spider_update_history_command(args)
        else:
            success = False
            
        sys.exit(0 if success else 1)
    
    elif args.cmd == "demo":
        try:
            import asyncio
            
            # Handle Phase 3 demo
            if (args.phase == '3' or args.phase == 'all') and PHASE3_AVAILABLE:
                from .backend.discovery.phase3_demo import Phase3Demo
                
                async def run_phase3_demo():
                    demo = Phase3Demo()
                    
                    if args.component == 'ml-analysis':
                        await demo.demo_ml_content_analysis()
                    elif args.component == 'quality':
                        await demo.demo_data_quality_assessment()
                    elif args.component == 'patterns':
                        await demo.demo_intelligent_pattern_recognition()
                    elif args.component == 'discovery':
                        await demo.demo_predictive_discovery()
                    elif args.component == 'integration':
                        await demo.demo_system_integration()
                    else:
                        await demo.run_full_demo()
                
                if args.phase == '3':
                    asyncio.run(run_phase3_demo())
                    sys.exit(0)
            
            # Handle Phase 2 demo
            if (args.phase == '2' or args.phase == 'all') and PHASE2_AVAILABLE:
                from .backend.discovery.phase2_demo import Phase2Demo
                
                async def run_phase2_demo():
                    demo = Phase2Demo()
                    
                    if args.component == 'dom':
                        await demo.demo_dom_analysis()
                    elif args.component == 'changes':
                        await demo.demo_change_detection()
                    elif args.component == 'updates':
                        await demo.demo_spider_updates()
                    elif args.component == 'scheduling':
                        await demo.demo_scheduling_system()
                    elif args.component == 'integration':
                        demo.demo_phase2_integration()
                    else:
                        await demo.run_full_demo()
                
                if args.phase == '2':
                    asyncio.run(run_phase2_demo())
                    sys.exit(0)
                
                # Run Phase 2 first if doing all phases
                if args.phase == 'all':
                    print("🚀 Starting Phase 2 Demo...")
                    asyncio.run(run_phase2_demo())
                    print("\n" + "="*60 + "\n")
            
            # Run Phase 3 after Phase 2 if doing all phases
            if args.phase == 'all' and PHASE3_AVAILABLE:
                print("🚀 Starting Phase 3 Demo...")
                asyncio.run(run_phase3_demo())
            elif args.phase == 'all' and PHASE3_AVAILABLE:
                asyncio.run(run_phase3_demo())
            
            # Handle cases where requested phases aren't available
            if args.phase == '2' and not PHASE2_AVAILABLE:
                print("❌ Phase 2 components not available")
                sys.exit(1)
            elif args.phase == '3' and not PHASE3_AVAILABLE:
                print("❌ Phase 3 components not available")
                print("📦 Install required dependencies: pip install scikit-learn pandas numpy")
                sys.exit(1)
            elif args.phase == 'all' and not PHASE2_AVAILABLE and not PHASE3_AVAILABLE:
                print("❌ No demo phases available")
                sys.exit(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Demo cancelled by user")
            sys.exit(1)
    
    # Route Phase 3 commands
    elif args.cmd == "phase3":
        if PHASE3_AVAILABLE:
            try:
                # Import Phase 3 CLI functions
                if args.phase3_cmd == "analyze-content":
                    print("🔬 Starting ML content analysis...")
                    print("⚠️  Phase 3 CLI integration in progress")
                    print("💡 Use: python -m business_intel_scraper.backend.cli.phase3_commands analyze-content <url>")
                    
                elif args.phase3_cmd == "assess-quality":
                    print("📊 Starting ML quality assessment...")
                    print("⚠️  Phase 3 CLI integration in progress")
                    print("💡 Use: python -m business_intel_scraper.backend.cli.phase3_commands assess-quality <data_file>")
                    
                elif args.phase3_cmd == "learn-patterns":
                    print("🧠 Starting pattern learning...")
                    print("⚠️  Phase 3 CLI integration in progress")
                    print("💡 Use: python -m business_intel_scraper.backend.cli.phase3_commands learn-patterns <session_file>")
                    
                elif args.phase3_cmd == "discover-sources":
                    print("🔍 Starting predictive source discovery...")
                    print("⚠️  Phase 3 CLI integration in progress")
                    print("💡 Use: python -m business_intel_scraper.backend.cli.phase3_commands discover-sources <seed_url>")
                    
                elif args.phase3_cmd == "optimize-selectors":
                    print("⚙️ Starting selector optimization...")
                    print("⚠️  Phase 3 CLI integration in progress")
                    print("💡 Use: python -m business_intel_scraper.backend.cli.phase3_commands optimize-selectors <url> <selectors>")
                    
                elif args.phase3_cmd == "run-learning-cycle":
                    print("🔄 Starting adaptive learning cycle...")
                    print("⚠️  Phase 3 CLI integration in progress")
                    print("💡 Use: python -m business_intel_scraper.backend.cli.phase3_commands run-learning-cycle")
                    
                elif args.phase3_cmd == "generate-insights":
                    print("📈 Generating ML insights report...")
                    print("⚠️  Phase 3 CLI integration in progress")
                    print("💡 Use: python -m business_intel_scraper.backend.cli.phase3_commands generate-insights")
                    
                elif args.phase3_cmd == "status":
                    print("📋 Checking Phase 3 system status...")
                    # This one we can implement directly
                    try:
                        from .backend.discovery.ml_content_analysis import content_analyzer
                        from .backend.discovery.data_quality_assessment import quality_assessor  
                        from .backend.discovery.intelligent_pattern_recognition import pattern_recognizer
                        
                        print("\n🚀 Phase 3: Advanced Discovery System Status")
                        print("=" * 50)
                        
                        # Content analyzer
                        if content_analyzer is not None:
                            print("✅ ML Content Analyzer - Ready")
                        else:
                            print("❌ ML Content Analyzer - Not available")
                        
                        # Quality assessor
                        if quality_assessor is not None:
                            print("✅ Data Quality Assessor - Ready")
                        else:
                            print("❌ Data Quality Assessor - Not available")
                        
                        # Pattern recognizer
                        if pattern_recognizer is not None:
                            print("✅ Pattern Recognizer - Ready")
                            try:
                                stats = pattern_recognizer.get_pattern_statistics()
                                print(f"  • Patterns: {stats.get('total_patterns', 0)}")
                                print(f"  • Learning Sessions: {stats.get('learning_sessions', 0)}")
                            except Exception:
                                print("  • Pattern statistics unavailable")
                        else:
                            print("❌ Pattern Recognizer - Not available")
                        
                        # ML dependencies
                        try:
                            import sklearn
                            print("✅ scikit-learn - Available")
                        except ImportError:
                            print("⚠️ scikit-learn - Not available (fallback mode)")
                        
                        try:
                            import pandas
                            print("✅ pandas - Available")
                        except ImportError:
                            print("❌ pandas - Required for data processing")
                        
                        try:
                            import numpy
                            print("✅ numpy - Available")
                        except ImportError:
                            print("❌ numpy - Required for ML operations")
                        
                        print("\n🎯 Phase 3 Core Components:")
                        print("• ML-Powered Content Analysis")
                        print("• Advanced Data Quality Assessment") 
                        print("• Intelligent Pattern Recognition")
                        print("• Predictive Source Discovery")
                        print("• Adaptive Learning Algorithms")
                        
                    except Exception as e:
                        print(f"❌ Status check failed: {e}")
                    
                else:
                    print(f"❌ Unknown Phase 3 command: {args.phase3_cmd}")
                    sys.exit(1)
                    
            except KeyboardInterrupt:
                print("\n🛑 Phase 3 operation cancelled by user")
                sys.exit(1)
            except Exception as e:
                print(f"❌ Phase 3 operation failed: {e}")
                sys.exit(1)
        else:
            print("❌ Phase 3 components not available")
            print("📦 Install required dependencies: pip install scikit-learn pandas numpy")
            sys.exit(1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
