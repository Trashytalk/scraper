"""
Test runner script for Phase 1 and Phase 2 testing.

Provides organized test execution with reporting.
"""

#!/usr/bin/env python3

import sys
import subprocess
from pathlib import Path
import argparse


def run_tests(test_type="all", verbose=False, coverage=False):
    """Run specified test suites."""

    test_dir = Path(__file__).parent

    # Base pytest command
    cmd = ["python", "-m", "pytest"]

    if verbose:
        cmd.append("-v")

    if coverage:
        cmd.extend(
            ["--cov=business_intel_scraper", "--cov-report=html", "--cov-report=term"]
        )

    # Test selection based on type
    if test_type == "all":
        cmd.append(str(test_dir))
    elif test_type == "unit":
        cmd.extend(["-m", "unit", str(test_dir)])
    elif test_type == "integration":
        cmd.extend(["-m", "integration", str(test_dir)])
    elif test_type == "performance":
        cmd.extend(["-m", "performance", str(test_dir)])
    elif test_type == "phase1":
        cmd.append(str(test_dir / "phase1"))
    elif test_type == "phase2":
        cmd.append(str(test_dir / "phase2"))
    elif test_type == "load":
        cmd.extend(["-m", "load_test", str(test_dir)])
    else:
        print(f"Unknown test type: {test_type}")
        sys.exit(1)

    # Run tests
    print(f"Running {test_type} tests...")
    print(f"Command: {' '.join(cmd)}")

    result = subprocess.run(cmd)
    return result.returncode


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(
        description="Run Business Intelligence Scraper tests"
    )
    parser.add_argument(
        "test_type",
        choices=[
            "all",
            "unit",
            "integration",
            "performance",
            "phase1",
            "phase2",
            "load",
        ],
        default="all",
        nargs="?",
        help="Type of tests to run",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "--coverage", action="store_true", help="Generate coverage report"
    )

    args = parser.parse_args()

    # Run tests
    exit_code = run_tests(args.test_type, args.verbose, args.coverage)

    if exit_code == 0:
        print(f"\n✅ {args.test_type.title()} tests passed!")
    else:
        print(f"\n❌ {args.test_type.title()} tests failed!")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
