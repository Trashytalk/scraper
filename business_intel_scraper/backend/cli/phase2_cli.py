#!/usr/bin/env python3
"""
CLI commands for Phase 2: DOM Change Detection and Spider Updates
"""

import asyncio
import sys
import argparse
import json
from datetime import datetime, timedelta

from ..discovery.dom_change_detection import DOMChangeDetector, DOMAnalyzer
from ..discovery.spider_update_system import SpiderUpdater


def setup_dom_change_parser(subparsers):
    """Setup DOM change detection command parser"""
    parser = subparsers.add_parser("dom-changes", help="Manage DOM change detection")

    dom_subparsers = parser.add_subparsers(
        dest="dom_command", help="DOM change commands"
    )

    # Check for changes command
    check_parser = dom_subparsers.add_parser("check", help="Check URLs for DOM changes")
    check_parser.add_argument("--urls", nargs="*", help="URLs to check for changes")
    check_parser.add_argument("--file", help="File containing URLs (one per line)")
    check_parser.add_argument("--output", help="Output file for changes detected")

    # List changes command
    list_parser = dom_subparsers.add_parser("list", help="List detected changes")
    list_parser.add_argument("--url", help="Filter by specific URL")
    list_parser.add_argument(
        "--severity",
        choices=["low", "medium", "high", "critical"],
        help="Filter by severity",
    )
    list_parser.add_argument(
        "--days", type=int, default=7, help="Show changes from last N days"
    )
    list_parser.add_argument(
        "--output-format",
        choices=["table", "json"],
        default="table",
        help="Output format",
    )

    # Analyze page command
    analyze_parser = dom_subparsers.add_parser(
        "analyze", help="Analyze page DOM structure"
    )
    analyze_parser.add_argument("url", help="URL to analyze")
    analyze_parser.add_argument("--output", help="Output file for fingerprint data")

    # Report command
    report_parser = dom_subparsers.add_parser("report", help="Generate change report")
    report_parser.add_argument(
        "--days", type=int, default=7, help="Report period in days"
    )
    report_parser.add_argument("--output", help="Output file for report")


def setup_spider_update_parser(subparsers):
    """Setup spider update command parser"""
    parser = subparsers.add_parser("spider-updates", help="Manage spider updates")

    update_subparsers = parser.add_subparsers(
        dest="update_command", help="Spider update commands"
    )

    # Check and update command
    check_parser = update_subparsers.add_parser(
        "check", help="Check and update spiders"
    )
    check_parser.add_argument("--url", help="Check spiders for specific URL")
    check_parser.add_argument(
        "--severity",
        choices=["low", "medium", "high", "critical"],
        help="Process changes of specific severity",
    )
    check_parser.add_argument(
        "--auto-fix", action="store_true", help="Apply automatic fixes where possible"
    )
    check_parser.add_argument(
        "--backup",
        action="store_true",
        default=True,
        help="Create backup before updating (default: True)",
    )

    # Status command
    status_parser = update_subparsers.add_parser(
        "status", help="Show spider update status"
    )
    status_parser.add_argument(
        "--days", type=int, default=30, help="Status period in days"
    )

    # History command
    history_parser = update_subparsers.add_parser("history", help="Show update history")
    history_parser.add_argument(
        "--limit", type=int, default=10, help="Number of sessions to show"
    )


async def check_dom_changes_command(args):
    """Execute DOM change checking"""
    print("🔍 Checking for DOM changes...")

    # Get URLs to check
    urls = []
    if args.urls:
        urls.extend(args.urls)

    if args.file:
        try:
            with open(args.file, "r") as f:
                file_urls = [line.strip() for line in f if line.strip()]
                urls.extend(file_urls)
        except Exception as e:
            print(f"❌ Error reading URL file: {e}")
            return False

    if not urls:
        print("❌ No URLs provided. Use --urls or --file")
        return False

    detector = DOMChangeDetector()
    all_changes = []

    import aiohttp

    async with aiohttp.ClientSession() as session:
        for url in urls:
            try:
                print(f"📊 Checking {url}...")

                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        changes = await detector.check_for_changes(url, html_content)
                        all_changes.extend(changes)

                        print(f"   Found {len(changes)} changes")
                    else:
                        print(f"   ❌ HTTP {response.status}")

            except Exception as e:
                print(f"   ❌ Error: {e}")
                continue

    print(f"\n📋 Summary: {len(all_changes)} total changes detected")

    # Categorize changes
    by_severity = {}
    by_type = {}

    for change in all_changes:
        by_severity[change.severity] = by_severity.get(change.severity, 0) + 1
        by_type[change.change_type] = by_type.get(change.change_type, 0) + 1

    print(f"📊 By severity: {dict(by_severity)}")
    print(f"📊 By type: {dict(by_type)}")

    # Show critical changes
    critical_changes = [c for c in all_changes if c.severity == "critical"]
    if critical_changes:
        print("\n🚨 Critical Changes:")
        for change in critical_changes:
            print(f"   • {change.url}")
            print(f"     {change.description}")
            if change.suggested_fixes:
                print(f"     Fix: {change.suggested_fixes[0]}")
            print()

    # Save output if requested
    if args.output:
        output_data = [change.to_dict() for change in all_changes]
        with open(args.output, "w") as f:
            json.dump(output_data, f, indent=2)
        print(f"💾 Results saved to {args.output}")

    return True


def list_dom_changes_command(args):
    """List detected DOM changes"""
    detector = DOMChangeDetector()

    # Filter changes
    cutoff_date = datetime.utcnow() - timedelta(days=args.days)
    changes = [c for c in detector.changes if c.detected_at > cutoff_date]

    if args.url:
        changes = [c for c in changes if c.url == args.url]

    if args.severity:
        changes = [c for c in changes if c.severity == args.severity]

    if not changes:
        print("No changes found matching criteria")
        return True

    if args.output_format == "json":
        # JSON output
        output_data = [change.to_dict() for change in changes]
        print(json.dumps(output_data, indent=2))
    else:
        # Table output
        print(f"\n📋 Found {len(changes)} DOM changes:")
        print("-" * 120)
        print(
            f"{'URL':<40} {'Type':<12} {'Severity':<8} {'Date':<16} {'Description':<40}"
        )
        print("-" * 120)

        for change in sorted(changes, key=lambda x: x.detected_at, reverse=True):
            url_display = (
                change.url[:37] + "..." if len(change.url) > 40 else change.url
            )
            desc_display = (
                change.description[:37] + "..."
                if len(change.description) > 40
                else change.description
            )
            date_display = change.detected_at.strftime("%Y-%m-%d %H:%M")

            print(
                f"{url_display:<40} {change.change_type:<12} {change.severity:<8} "
                f"{date_display:<16} {desc_display:<40}"
            )

    return True


async def analyze_page_command(args):
    """Analyze page DOM structure"""
    print(f"🔍 Analyzing DOM structure for {args.url}...")

    analyzer = DOMAnalyzer()

    try:
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.get(args.url, timeout=30) as response:
                if response.status == 200:
                    html_content = await response.text()
                    fingerprint = await analyzer.analyze_page(args.url, html_content)

                    print("✅ Analysis complete")
                    print(f"   Structure hash: {fingerprint.structure_hash}")
                    print(
                        f"   Total elements: {sum(fingerprint.element_counts.values())}"
                    )
                    print(f"   Key selectors: {len(fingerprint.key_selectors)}")
                    print(f"   Forms found: {len(fingerprint.form_signatures)}")
                    print(f"   API endpoints: {len(fingerprint.api_endpoints)}")

                    # Show top element types
                    top_elements = sorted(
                        fingerprint.element_counts.items(),
                        key=lambda x: x[1],
                        reverse=True,
                    )[:5]
                    print(f"   Top elements: {dict(top_elements)}")

                    # Show key selectors
                    if fingerprint.key_selectors:
                        print("\n🎯 Key Selectors Found:")
                        for selector, content in list(
                            fingerprint.key_selectors.items()
                        )[:5]:
                            print(f"   {selector}: {content[:60]}...")

                    # Show forms
                    if fingerprint.form_signatures:
                        print("\n📝 Forms Found:")
                        for i, form in enumerate(fingerprint.form_signatures):
                            print(
                                f"   Form {i+1}: {form['method'].upper()} {form['action']}"
                            )
                            print(f"   Fields: {len(form['fields'])}")

                    # Show API endpoints
                    if fingerprint.api_endpoints:
                        print("\n🔌 API Endpoints Found:")
                        for endpoint in fingerprint.api_endpoints[:5]:
                            print(f"   {endpoint}")

                    # Save output if requested
                    if args.output:
                        with open(args.output, "w") as f:
                            json.dump(fingerprint.to_dict(), f, indent=2)
                        print(f"\n💾 Fingerprint saved to {args.output}")

                    return True

                else:
                    print(f"❌ HTTP {response.status}")
                    return False

    except Exception as e:
        print(f"❌ Error analyzing page: {e}")
        return False


def generate_dom_report_command(args):
    """Generate DOM change report"""
    print(f"📊 Generating DOM change report for last {args.days} days...")

    detector = DOMChangeDetector()

    # Filter changes by date
    cutoff_date = datetime.utcnow() - timedelta(days=args.days)
    recent_changes = [c for c in detector.changes if c.detected_at > cutoff_date]

    # Generate report
    report = {
        "generated_at": datetime.utcnow().isoformat(),
        "period_days": args.days,
        "summary": {
            "total_changes": len(recent_changes),
            "urls_affected": len(set(c.url for c in recent_changes)),
            "by_severity": {},
            "by_type": {},
            "auto_fixable": len([c for c in recent_changes if c.auto_fixable]),
            "manual_review": len([c for c in recent_changes if not c.auto_fixable]),
        },
        "top_affected_urls": {},
        "recent_critical_changes": [],
    }

    # Analyze changes
    for change in recent_changes:
        # Count by severity
        report["summary"]["by_severity"][change.severity] = (
            report["summary"]["by_severity"].get(change.severity, 0) + 1
        )

        # Count by type
        report["summary"]["by_type"][change.change_type] = (
            report["summary"]["by_type"].get(change.change_type, 0) + 1
        )

        # Count by URL
        report["top_affected_urls"][change.url] = (
            report["top_affected_urls"].get(change.url, 0) + 1
        )

    # Get critical changes
    critical_changes = [c for c in recent_changes if c.severity == "critical"]
    for change in critical_changes[-5:]:  # Last 5 critical changes
        report["recent_critical_changes"].append(
            {
                "url": change.url,
                "description": change.description,
                "detected_at": change.detected_at.isoformat(),
                "suggested_fixes": change.suggested_fixes,
            }
        )

    # Sort top affected URLs
    report["top_affected_urls"] = dict(
        sorted(report["top_affected_urls"].items(), key=lambda x: x[1], reverse=True)[
            :10
        ]
    )

    print("✅ Report generated")
    print(f"   Total changes: {report['summary']['total_changes']}")
    print(f"   URLs affected: {report['summary']['urls_affected']}")
    print(f"   By severity: {report['summary']['by_severity']}")
    print(f"   Auto-fixable: {report['summary']['auto_fixable']}")

    # Save report
    if args.output:
        with open(args.output, "w") as f:
            json.dump(report, f, indent=2)
        print(f"💾 Report saved to {args.output}")
    else:
        print("\n📋 Report Summary:")
        print(json.dumps(report, indent=2))

    return True


async def check_spider_updates_command(args):
    """Check and update spiders"""
    print("🔧 Checking spider updates...")

    detector = DOMChangeDetector()
    updater = SpiderUpdater()

    # Get changes to process
    changes = []

    if args.url:
        changes = detector.get_changes_for_url(args.url, days=7)
    elif args.severity:
        changes = detector.get_changes_by_severity(args.severity, days=7)
    else:
        # Get high-priority changes
        changes = detector.get_critical_changes(days=1)
        changes.extend(detector.get_changes_by_severity("high", days=3))

    if not changes:
        print("No changes found requiring spider updates")
        return True

    print(f"📋 Found {len(changes)} changes to process")

    # Process updates
    if args.auto_fix:
        update_results = await updater.update_spiders_for_changes(changes)

        print("✅ Update completed:")
        print(f"   Spiders updated: {update_results['spiders_updated']}")
        print(f"   Automatic fixes: {update_results['automatic_fixes']}")
        print(f"   Manual review needed: {update_results['manual_review_needed']}")
        print(f"   Failed updates: {update_results['failed_updates']}")

        # Show specific updates
        for update in update_results["updates"]:
            print(f"\n🔧 Spider: {update['spider_name']}")

            for mod in update.get("modifications", []):
                status = "✅ Applied" if mod["automatic"] else "📋 Manual"
                print(f"   {status}: {mod['description']}")

            for warning in update.get("warnings", []):
                print(f"   ⚠️ {warning}")
    else:
        # Just show what would be updated
        print("📋 Changes that would trigger updates:")
        for change in changes[:10]:  # Show first 10
            print(f"   • {change.url}")
            print(
                f"     {change.change_type} [{change.severity}]: {change.description}"
            )
            if change.auto_fixable:
                print(
                    f"     ✅ Auto-fixable: {change.suggested_fixes[0] if change.suggested_fixes else 'Generic fix'}"
                )
            else:
                print("     📋 Manual review needed")
            print()

        print("\nUse --auto-fix to apply automatic updates")

    return True


def spider_update_status_command(args):
    """Show spider update status"""
    updater = SpiderUpdater()

    stats = updater.get_update_statistics(days=args.days)

    print(f"📊 Spider Update Statistics (last {args.days} days)")
    print("-" * 50)
    print(f"Total update sessions: {stats['total_sessions']}")
    print(f"Spiders updated: {stats['total_spiders_updated']}")
    print(f"Automatic fixes: {stats['total_automatic_fixes']}")
    print(f"Average success rate: {stats['average_success_rate']:.1f}%")

    if stats["most_common_change_types"]:
        print("\n📋 Most common change types:")
        for change_type, count in list(stats["most_common_change_types"].items())[:5]:
            print(f"   {change_type}: {count}")

    return True


def spider_update_history_command(args):
    """Show spider update history"""
    updater = SpiderUpdater()

    history = updater.update_history[-args.limit :]

    if not history:
        print("No update history found")
        return True

    print(f"📈 Spider Update History (last {args.limit} sessions)")
    print("-" * 80)

    for session in reversed(history):  # Most recent first
        timestamp = datetime.fromisoformat(session["timestamp"])
        print(f"🕐 {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Spiders updated: {session['spiders_updated']}")
        print(f"   Automatic fixes: {session['automatic_fixes']}")
        print(f"   Success rate: {session.get('success_rate', 0):.1f}%")

        if session.get("updates"):
            for update in session["updates"][:3]:  # Show first 3 updates
                print(
                    f"   • {update['spider_name']}: {update['changes_processed']} changes"
                )
        print()

    return True


def main():
    """Main CLI entry point for Phase 2 commands"""
    parser = argparse.ArgumentParser(description="Phase 2: DOM Change Detection CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    setup_dom_change_parser(subparsers)
    setup_spider_update_parser(subparsers)

    args = parser.parse_args()

    if not hasattr(args, "dom_command") and not hasattr(args, "update_command"):
        parser.print_help()
        return False

    # Route to appropriate handler
    try:
        if hasattr(args, "dom_command") and args.dom_command:
            if args.dom_command == "check":
                return asyncio.run(check_dom_changes_command(args))
            elif args.dom_command == "list":
                return list_dom_changes_command(args)
            elif args.dom_command == "analyze":
                return asyncio.run(analyze_page_command(args))
            elif args.dom_command == "report":
                return generate_dom_report_command(args)

        elif hasattr(args, "update_command") and args.update_command:
            if args.update_command == "check":
                return asyncio.run(check_spider_updates_command(args))
            elif args.update_command == "status":
                return spider_update_status_command(args)
            elif args.update_command == "history":
                return spider_update_history_command(args)

        else:
            print("Unknown command")
            return False

    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
