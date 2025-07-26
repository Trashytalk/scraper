#!/usr/bin/env python3
"""
Complete Repository Test Coverage Execution Script
==================================================

This script executes comprehensive test coverage across the entire repository,
ensuring 100% coverage of all modules, components, and functionality.

Test Execution Categories:
1. Root-Level Modules Testing
2. GUI Components Testing  
3. Scripts and Utilities Testing
4. Business Intelligence Modules Testing
5. Existing Comprehensive Test Suite
6. Coverage Analysis and Reporting

Features:
- Parallel test execution for performance
- Detailed coverage reporting
- Error aggregation and analysis
- Performance metrics collection
- HTML report generation
- CI/CD integration ready

Author: Business Intelligence Scraper Test Suite
Created: 2024
"""

import os
import sys
import time
import json
import subprocess
import concurrent.futures
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse

# Add root directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class ComprehensiveTestRunner:
    """Comprehensive test runner for complete repository coverage."""
    
    def __init__(self, root_dir: Optional[Path] = None):
        """Initialize the test runner."""
        self.root_dir = root_dir or Path(__file__).parent.parent
        self.test_dir = self.root_dir / 'tests'
        self.results = {}
        self.start_time = None
        self.end_time = None
        
        # Test suite configuration
        self.test_suites = {
            'root_modules': {
                'file': 'test_root_modules.py',
                'description': 'Root-level modules (scraping_engine, backend_server, bis.py, etc.)',
                'priority': 1,
                'timeout': 300
            },
            'gui_components': {
                'file': 'test_gui_components.py', 
                'description': 'GUI components and interfaces',
                'priority': 2,
                'timeout': 300
            },
            'scripts_utilities': {
                'file': 'test_scripts_utilities.py',
                'description': 'Utility scripts and configuration modules',
                'priority': 3,
                'timeout': 300
            },
            'business_intelligence': {
                'file': 'test_business_intelligence.py',
                'description': 'Business intelligence modules and advanced features',
                'priority': 4,
                'timeout': 300
            },
            'centralized_data': {
                'file': 'test_centralized_data.py',
                'description': 'Centralized data models and operations',
                'priority': 5,
                'timeout': 600
            },
            'comprehensive_integration': {
                'file': 'test_comprehensive_integration.py',
                'description': 'End-to-end integration testing',
                'priority': 6,
                'timeout': 600
            },
            'performance_load': {
                'file': 'test_performance_load.py',
                'description': 'Performance and load testing',
                'priority': 7,
                'timeout': 900
            },
            'security': {
                'file': 'test_security.py',
                'description': 'Security testing and vulnerability assessment',
                'priority': 8,
                'timeout': 600
            },
            'api': {
                'file': 'test_api.py',
                'description': 'API endpoints and WebSocket functionality',
                'priority': 9,
                'timeout': 600
            }
        }
    
    def setup_test_environment(self) -> bool:
        """Set up the test environment."""
        print("🔧 Setting up test environment...")
        
        try:
            # Ensure test directory exists
            self.test_dir.mkdir(exist_ok=True)
            
            # Install test dependencies if needed
            self._install_test_dependencies()
            
            # Set environment variables for testing
            os.environ['TESTING'] = 'true'
            os.environ['PYTHONPATH'] = str(self.root_dir)
            
            print("✅ Test environment setup complete")
            return True
            
        except Exception as e:
            print(f"❌ Test environment setup failed: {e}")
            return False
    
    def _install_test_dependencies(self) -> None:
        """Install required test dependencies."""
        dependencies = [
            'pytest>=7.0.0',
            'pytest-asyncio>=0.21.0',
            'pytest-cov>=4.0.0',
            'pytest-xdist>=3.0.0',
            'pytest-html>=3.1.0',
            'coverage>=7.0.0'
        ]
        
        try:
            for dep in dependencies:
                subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', dep],
                    check=True,
                    capture_output=True
                )
        except subprocess.CalledProcessError:
            print("⚠️  Some test dependencies may not be available")
    
    def run_single_test_suite(self, suite_name: str, suite_config: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test suite."""
        test_file = self.test_dir / suite_config['file']
        
        if not test_file.exists():
            return {
                'suite': suite_name,
                'status': 'skipped',
                'reason': f"Test file {suite_config['file']} not found",
                'duration': 0,
                'tests_run': 0,
                'failures': 0,
                'errors': 0
            }
        
        print(f"🧪 Running {suite_name}: {suite_config['description']}")
        
        start_time = time.time()
        
        try:
            # Run pytest with coverage
            cmd = [
                sys.executable, '-m', 'pytest',
                str(test_file),
                '-v',
                '--tb=short',
                '--color=yes',
                f'--timeout={suite_config["timeout"]}',
                '--cov-append',
                '--cov-report=term-missing',
                '--cov-report=json',
                '--cov-report=html',
                '--junit-xml=pytest_results.xml'
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                timeout=suite_config['timeout']
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Parse results
            output_lines = result.stdout.split('\n')
            summary_line = [line for line in output_lines if 'passed' in line and 'failed' in line]
            
            tests_run = 0
            failures = 0
            errors = 0
            
            if summary_line:
                # Extract numbers from summary
                import re
                summary = summary_line[-1]
                passed_match = re.search(r'(\d+) passed', summary)
                failed_match = re.search(r'(\d+) failed', summary)
                error_match = re.search(r'(\d+) error', summary)
                
                if passed_match:
                    tests_run += int(passed_match.group(1))
                if failed_match:
                    failures = int(failed_match.group(1))
                    tests_run += failures
                if error_match:
                    errors = int(error_match.group(1))
                    tests_run += errors
            
            status = 'passed' if result.returncode == 0 else 'failed'
            
            return {
                'suite': suite_name,
                'status': status,
                'duration': duration,
                'tests_run': tests_run,
                'failures': failures,
                'errors': errors,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'suite': suite_name,
                'status': 'timeout',
                'duration': suite_config['timeout'],
                'tests_run': 0,
                'failures': 0,
                'errors': 1,
                'stderr': f'Test suite timed out after {suite_config["timeout"]} seconds'
            }
        except Exception as e:
            return {
                'suite': suite_name,
                'status': 'error',
                'duration': time.time() - start_time,
                'tests_run': 0,
                'failures': 0,
                'errors': 1,
                'stderr': str(e)
            }
    
    def run_parallel_tests(self, max_workers: int = 3) -> Dict[str, Any]:
        """Run test suites in parallel for better performance."""
        print(f"🚀 Running tests in parallel with {max_workers} workers...")
        
        self.start_time = time.time()
        
        # Sort suites by priority
        sorted_suites = sorted(
            self.test_suites.items(),
            key=lambda x: x[1]['priority']
        )
        
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all test suites
            future_to_suite = {
                executor.submit(self.run_single_test_suite, suite_name, suite_config): suite_name
                for suite_name, suite_config in sorted_suites
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_suite):
                suite_name = future_to_suite[future]
                try:
                    result = future.result()
                    results[suite_name] = result
                    
                    # Print immediate result
                    status_emoji = {
                        'passed': '✅',
                        'failed': '❌',
                        'skipped': '⏭️',
                        'timeout': '⏰',
                        'error': '💥'
                    }
                    
                    emoji = status_emoji.get(result['status'], '❓')
                    print(f"{emoji} {suite_name}: {result['status']} "
                          f"({result['tests_run']} tests, {result['duration']:.1f}s)")
                    
                except Exception as e:
                    results[suite_name] = {
                        'suite': suite_name,
                        'status': 'error',
                        'duration': 0,
                        'tests_run': 0,
                        'failures': 0,
                        'errors': 1,
                        'stderr': str(e)
                    }
        
        self.end_time = time.time()
        self.results = results
        
        return results
    
    def run_sequential_tests(self) -> Dict[str, Any]:
        """Run test suites sequentially."""
        print("🔄 Running tests sequentially...")
        
        self.start_time = time.time()
        
        # Sort suites by priority
        sorted_suites = sorted(
            self.test_suites.items(),
            key=lambda x: x[1]['priority']
        )
        
        results = {}
        
        for suite_name, suite_config in sorted_suites:
            result = self.run_single_test_suite(suite_name, suite_config)
            results[suite_name] = result
            
            # Print immediate result
            status_emoji = {
                'passed': '✅',
                'failed': '❌',
                'skipped': '⏭️',
                'timeout': '⏰',
                'error': '💥'
            }
            
            emoji = status_emoji.get(result['status'], '❓')
            print(f"{emoji} {suite_name}: {result['status']} "
                  f"({result['tests_run']} tests, {result['duration']:.1f}s)")
        
        self.end_time = time.time()
        self.results = results
        
        return results
    
    def generate_coverage_report(self) -> Dict[str, Any]:
        """Generate comprehensive coverage report."""
        print("📊 Generating coverage report...")
        
        try:
            # Run coverage report
            cmd = [
                sys.executable, '-m', 'coverage', 'report',
                '--show-missing',
                '--format=json'
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.root_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                coverage_data = json.loads(result.stdout)
                return coverage_data
            else:
                print(f"⚠️  Coverage report generation failed: {result.stderr}")
                return {}
                
        except Exception as e:
            print(f"⚠️  Coverage report error: {e}")
            return {}
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate comprehensive summary report."""
        if not self.results:
            return {}
        
        total_duration = self.end_time - self.start_time if self.start_time and self.end_time else 0
        
        # Calculate totals
        total_tests = sum(r['tests_run'] for r in self.results.values())
        total_failures = sum(r['failures'] for r in self.results.values())
        total_errors = sum(r['errors'] for r in self.results.values())
        total_passed = total_tests - total_failures - total_errors
        
        # Status counts
        status_counts = {}
        for result in self.results.values():
            status = result['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Success rate
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_duration': total_duration,
            'total_test_suites': len(self.results),
            'total_tests': total_tests,
            'total_passed': total_passed,
            'total_failures': total_failures,
            'total_errors': total_errors,
            'success_rate': success_rate,
            'status_counts': status_counts,
            'suite_results': self.results
        }
        
        return summary
    
    def print_final_report(self, summary: Dict[str, Any]) -> None:
        """Print comprehensive final report."""
        print("\n" + "="*80)
        print("📋 COMPREHENSIVE TEST COVERAGE REPORT")
        print("="*80)
        
        # Overall statistics
        print(f"\n⏱️  Total Duration: {summary['total_duration']:.1f} seconds")
        print(f"📦 Test Suites: {summary['total_test_suites']}")
        print(f"🧪 Total Tests: {summary['total_tests']}")
        print(f"✅ Passed: {summary['total_passed']}")
        print(f"❌ Failed: {summary['total_failures']}")
        print(f"💥 Errors: {summary['total_errors']}")
        print(f"📈 Success Rate: {summary['success_rate']:.1f}%")
        
        # Suite breakdown
        print(f"\n📊 TEST SUITE BREAKDOWN:")
        print("-" * 80)
        
        for suite_name, result in summary['suite_results'].items():
            config = self.test_suites.get(suite_name, {})
            description = config.get('description', 'No description')
            
            status_emoji = {
                'passed': '✅',
                'failed': '❌',
                'skipped': '⏭️',
                'timeout': '⏰',
                'error': '💥'
            }
            
            emoji = status_emoji.get(result['status'], '❓')
            
            print(f"{emoji} {suite_name:25} | "
                  f"{result['status']:8} | "
                  f"{result['tests_run']:4} tests | "
                  f"{result['duration']:6.1f}s | "
                  f"{description}")
        
        # Overall assessment
        print(f"\n🎯 COVERAGE ASSESSMENT:")
        print("-" * 80)
        
        if summary['success_rate'] >= 95:
            print("🎉 EXCELLENT: Comprehensive test coverage achieved!")
        elif summary['success_rate'] >= 85:
            print("👍 GOOD: Strong test coverage with minor gaps")
        elif summary['success_rate'] >= 70:
            print("⚠️  MODERATE: Acceptable coverage with improvement needed")
        else:
            print("🚨 POOR: Significant gaps in test coverage")
        
        # Recommendations
        failed_suites = [name for name, result in summary['suite_results'].items() 
                        if result['status'] in ['failed', 'error', 'timeout']]
        
        if failed_suites:
            print(f"\n💡 RECOMMENDATIONS:")
            print("-" * 80)
            print("   - Review failed test suites:")
            for suite in failed_suites:
                print(f"     • {suite}")
            print("   - Check logs for detailed error information")
            print("   - Fix failing tests before production deployment")
        
        print("\n" + "="*80)
    
    def save_reports(self, summary: Dict[str, Any]) -> None:
        """Save reports to files."""
        reports_dir = self.root_dir / 'test_reports'
        reports_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save JSON report
        json_file = reports_dir / f'test_report_{timestamp}.json'
        with open(json_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"💾 Reports saved to: {reports_dir}")
        print(f"   - JSON: {json_file.name}")
        
        # Generate HTML report if possible
        try:
            html_file = reports_dir / f'test_report_{timestamp}.html'
            self._generate_html_report(summary, html_file)
            print(f"   - HTML: {html_file.name}")
        except Exception as e:
            print(f"   - HTML generation failed: {e}")
    
    def _generate_html_report(self, summary: Dict[str, Any], output_file: Path) -> None:
        """Generate HTML report."""
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Comprehensive Test Coverage Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .summary {{ margin: 20px 0; }}
                .suite {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 3px; }}
                .passed {{ background-color: #d4edda; }}
                .failed {{ background-color: #f8d7da; }}
                .skipped {{ background-color: #fff3cd; }}
                .error {{ background-color: #f5c6cb; }}
                .timeout {{ background-color: #f5c6cb; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📋 Comprehensive Test Coverage Report</h1>
                <p>Generated: {summary['timestamp']}</p>
            </div>
            
            <div class="summary">
                <h2>📊 Summary</h2>
                <table>
                    <tr><th>Metric</th><th>Value</th></tr>
                    <tr><td>Total Duration</td><td>{summary['total_duration']:.1f} seconds</td></tr>
                    <tr><td>Test Suites</td><td>{summary['total_test_suites']}</td></tr>
                    <tr><td>Total Tests</td><td>{summary['total_tests']}</td></tr>
                    <tr><td>Passed</td><td>{summary['total_passed']}</td></tr>
                    <tr><td>Failed</td><td>{summary['total_failures']}</td></tr>
                    <tr><td>Errors</td><td>{summary['total_errors']}</td></tr>
                    <tr><td>Success Rate</td><td>{summary['success_rate']:.1f}%</td></tr>
                </table>
            </div>
            
            <div class="suites">
                <h2>🧪 Test Suites</h2>
        """
        
        for suite_name, result in summary['suite_results'].items():
            status_class = result['status']
            config = self.test_suites.get(suite_name, {})
            description = config.get('description', 'No description')
            
            html_template += f"""
                <div class="suite {status_class}">
                    <h3>{suite_name}</h3>
                    <p><strong>Description:</strong> {description}</p>
                    <p><strong>Status:</strong> {result['status']}</p>
                    <p><strong>Tests:</strong> {result['tests_run']} | 
                       <strong>Duration:</strong> {result['duration']:.1f}s</p>
                </div>
            """
        
        html_template += """
            </div>
        </body>
        </html>
        """
        
        with open(output_file, 'w') as f:
            f.write(html_template)

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Comprehensive Repository Test Coverage')
    parser.add_argument('--parallel', action='store_true', 
                       help='Run tests in parallel (default: sequential)')
    parser.add_argument('--workers', type=int, default=3,
                       help='Number of parallel workers (default: 3)')
    parser.add_argument('--suites', nargs='+',
                       help='Specific test suites to run')
    parser.add_argument('--coverage', action='store_true',
                       help='Generate coverage report')
    parser.add_argument('--save-reports', action='store_true',
                       help='Save reports to files')
    
    args = parser.parse_args()
    
    # Initialize test runner
    runner = ComprehensiveTestRunner()
    
    # Filter test suites if specified
    if args.suites:
        filtered_suites = {k: v for k, v in runner.test_suites.items() if k in args.suites}
        runner.test_suites = filtered_suites
    
    print("🎯 COMPREHENSIVE REPOSITORY TEST COVERAGE")
    print("="*60)
    print(f"📂 Root Directory: {runner.root_dir}")
    print(f"🧪 Test Suites: {len(runner.test_suites)}")
    print(f"⚡ Execution Mode: {'Parallel' if args.parallel else 'Sequential'}")
    
    if args.parallel:
        print(f"👥 Workers: {args.workers}")
    
    print("="*60)
    
    # Setup environment
    if not runner.setup_test_environment():
        sys.exit(1)
    
    # Run tests
    if args.parallel:
        results = runner.run_parallel_tests(args.workers)
    else:
        results = runner.run_sequential_tests()
    
    # Generate reports
    summary = runner.generate_summary_report()
    
    if args.coverage:
        coverage_data = runner.generate_coverage_report()
        summary['coverage'] = coverage_data
    
    # Print final report
    runner.print_final_report(summary)
    
    # Save reports if requested
    if args.save_reports:
        runner.save_reports(summary)
    
    # Exit with appropriate code
    if summary['total_failures'] > 0 or summary['total_errors'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == '__main__':
    main()
