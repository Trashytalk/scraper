"""
Enhanced CLI with Click framework
Provides comprehensive command-line interface for the Business Intelligence Scraper
"""

import os
import time
from pathlib import Path

import click

# Set up environment
os.environ.setdefault("PYTHONPATH", str(Path(__file__).parent))

from business_intel_scraper.backend.ai.cli import ai
from business_intel_scraper.backend.marketplace.cli import marketplace

# Import analytics CLI commands
try:
    from business_intel_scraper.backend.analytics.cli import analytics
except ImportError:
    analytics = None


@click.group()
@click.version_option()
def cli():
    """Business Intelligence Scraper CLI

    A comprehensive tool for web scraping, data analysis, and intelligence gathering.
    """
    pass


@cli.command()
@click.option("--host", default="localhost", help="Host to run the server on")
@click.option("--port", default=8000, help="Port to run the server on")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
def serve(host: str, port: int, reload: bool):
    """Start the API server"""
    import uvicorn

    click.echo(f"Starting Business Intelligence Scraper API on {host}:{port}")
    if reload:
        click.echo("Auto-reload enabled for development")

    uvicorn.run(
        "business_intel_scraper.backend.api.main:app",
        host=host,
        port=port,
        reload=reload,
    )


@cli.command()
@click.option(
    "--frontend", is_flag=True, help="Also start the frontend development server"
)
def dev(frontend: bool):
    """Start development servers"""
    import subprocess
    import threading

    click.echo("Starting development environment...")

    # Start API server in background
    def start_api():
        import uvicorn

        uvicorn.run(
            "business_intel_scraper.backend.api.main:app",
            host="localhost",
            port=8000,
            reload=True,
        )

    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()

    click.echo("✓ API server starting on http://localhost:8000")

    if frontend:
        frontend_dir = Path(__file__).parent / "frontend"
        if frontend_dir.exists():
            click.echo("✓ Frontend server starting on http://localhost:3000")
            try:
                subprocess.run(["npm", "run", "dev"], cwd=frontend_dir)
            except KeyboardInterrupt:
                click.echo("\nShutting down development servers...")
        else:
            click.echo("Frontend directory not found")
    else:
        try:
            click.echo("Press Ctrl+C to stop the server")
            while True:
                pass
        except KeyboardInterrupt:
            click.echo("\nShutting down API server...")


@cli.command()
def setup():
    """Run initial setup and configuration"""
    import subprocess
    import sys

    setup_script = Path(__file__).parent / "setup.sh"
    if setup_script.exists():
        click.echo("Running setup script...")
        try:
            subprocess.run([str(setup_script)], check=True)
        except subprocess.CalledProcessError as e:
            click.echo(f"Setup failed: {e}", err=True)
            sys.exit(1)
    else:
        click.echo("Setup script not found. Please run setup.sh manually.")


@cli.command()
@click.argument("project_name")
@click.option(
    "--template",
    "-t",
    type=click.Choice(["basic", "advanced", "enterprise", "research"]),
    default="basic",
    help="Project template to use",
)
@click.option("--target-dir", help="Target directory (default: current directory)")
def create(project_name: str, template: str, target_dir: str):
    """Create a new scraping project from template"""
    import subprocess

    create_script = Path(__file__).parent / "create-project.sh"
    if create_script.exists():
        cmd = [str(create_script), project_name, template]
        if target_dir:
            cmd.append(target_dir)

        click.echo(f"Creating {template} project: {project_name}")
        try:
            subprocess.run(cmd, check=True)
            click.echo(f"✓ Project {project_name} created successfully!")
        except subprocess.CalledProcessError as e:
            click.echo(f"Project creation failed: {e}", err=True)
    else:
        click.echo("Project creation script not found.")


@cli.command()
def status():
    """Show system status and health"""
    import httpx

    try:
        # Check API health
        response = httpx.get("http://localhost:8000/health", timeout=5.0)
        if response.status_code == 200:
            click.echo("✓ API Server: Running")
            health_data = response.json()
            click.echo(f"  Status: {health_data.get('status', 'unknown')}")
            click.echo(f"  Version: {health_data.get('version', 'unknown')}")
        else:
            click.echo("✗ API Server: Error")
    except Exception:
        click.echo("✗ API Server: Not running")

    # Check AI system
    try:
        response = httpx.get("http://localhost:8000/ai/health", timeout=5.0)
        if response.status_code == 200:
            ai_health = response.json()
            click.echo(f"✓ AI System: {ai_health.get('status', 'unknown')}")
        else:
            click.echo("✗ AI System: Error")
    except Exception:
        click.echo("✗ AI System: Not available")

    # Check database
    try:
        import sqlite3

        db_path = Path(__file__).parent / "data" / "scraper.db"
        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            conn.execute("SELECT 1")
            conn.close()
            click.echo("✓ Database: Connected")
        else:
            click.echo("- Database: Not initialized")
    except Exception:
        click.echo("✗ Database: Error")


@cli.command()
@click.option("--include-ai", is_flag=True, help="Include AI dependencies")
@click.option("--include-dev", is_flag=True, help="Include development dependencies")
def install(include_ai: bool, include_dev: bool):
    """Install dependencies"""
    import subprocess
    import sys

    click.echo("Installing dependencies...")

    # Base requirements
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True,
        )
        click.echo("✓ Base dependencies installed")
    except subprocess.CalledProcessError:
        click.echo("✗ Failed to install base dependencies", err=True)
        return

    # AI requirements (now included in main requirements.txt)
    if include_ai:
        click.echo("✓ AI dependencies included in main requirements")

    # Dev requirements (now included in main requirements.txt)
    if include_dev:
        click.echo("✓ Development dependencies included in main requirements")


@cli.command()
@click.option("--coverage", is_flag=True, help="Run with coverage report")
def test(coverage: bool):
    """Run the test suite"""
    import subprocess
    import sys

    if coverage:
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            "--cov=business_intel_scraper",
            "--cov-report=html",
            "--cov-report=term",
        ]
    else:
        cmd = [sys.executable, "-m", "pytest"]

    try:
        subprocess.run(cmd, check=True)
        if coverage:
            click.echo("Coverage report generated in htmlcov/")
    except subprocess.CalledProcessError:
        click.echo("Tests failed", err=True)


@cli.command()
def docs():
    """Generate and serve documentation"""
    import threading
    import webbrowser
    from http.server import HTTPServer, SimpleHTTPRequestHandler

    docs_dir = Path(__file__).parent / "docs"
    if not docs_dir.exists():
        click.echo("Documentation directory not found")
        return

    # Start simple HTTP server for docs
    os.chdir(docs_dir)

    def serve_docs():
        server = HTTPServer(("localhost", 8080), SimpleHTTPRequestHandler)
        server.serve_forever()

    server_thread = threading.Thread(target=serve_docs, daemon=True)
    server_thread.start()

    click.echo("Documentation server started at http://localhost:8080")

    # Open browser
    try:
        webbrowser.open("http://localhost:8080")
    except Exception as e:
        click.echo(f"Could not open browser automatically: {e}")
        click.echo("Please manually navigate to http://localhost:8080")

    try:
        click.echo("Press Ctrl+C to stop the documentation server")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        click.echo("\nShutting down documentation server...")


# Add subcommands
cli.add_command(marketplace)
cli.add_command(ai)

# Add analytics command if available
if analytics:
    cli.add_command(analytics)


if __name__ == "__main__":
    cli()
