#!/bin/bash

# Business Intelligence Scraper - Frontend Development Setup
# This script helps manage the frontend development environment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR"

echo "🚀 Business Intelligence Scraper - Frontend Management"
echo "======================================================"

show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  install     Install dependencies"
    echo "  dev         Start development server"
    echo "  build       Build for production"
    echo "  preview     Preview production build"
    echo "  test        Run tests"
    echo "  lint        Run linting"
    echo "  clean       Clean build artifacts"
    echo "  help        Show this help message"
    echo ""
}

install_deps() {
    echo "📦 Installing dependencies..."
    cd "$FRONTEND_DIR"
    npm install
    echo "✅ Dependencies installed successfully!"
}

start_dev() {
    echo "🏃 Starting development server..."
    echo "Frontend will be available at: http://localhost:3000"
    echo "API proxy will forward requests to: http://localhost:8000"
    echo ""
    echo "Press Ctrl+C to stop the server"
    cd "$FRONTEND_DIR"
    npm run dev
}

build_prod() {
    echo "🏗️  Building for production..."
    cd "$FRONTEND_DIR"
    npm run build
    echo "✅ Production build completed!"
    echo "📁 Build output is in: dist/"
}

preview_build() {
    echo "👀 Previewing production build..."
    cd "$FRONTEND_DIR"
    npm run preview
}

run_tests() {
    echo "🧪 Running tests..."
    cd "$FRONTEND_DIR"
    if [ -f "package.json" ] && grep -q '"test"' package.json; then
        npm test
    else
        echo "⚠️  No tests configured yet"
    fi
}

run_lint() {
    echo "🔍 Running linting..."
    cd "$FRONTEND_DIR"
    if [ -f "package.json" ] && grep -q '"lint"' package.json; then
        npm run lint
    else
        echo "⚠️  No linting configured yet"
    fi
}

clean_build() {
    echo "🧹 Cleaning build artifacts..."
    cd "$FRONTEND_DIR"
    rm -rf dist/
    rm -rf node_modules/.vite/
    echo "✅ Build artifacts cleaned!"
}

check_requirements() {
    if ! command -v node >/dev/null 2>&1; then
        echo "❌ Node.js is required but not installed."
        echo "Please install Node.js from https://nodejs.org/"
        exit 1
    fi

    if ! command -v npm >/dev/null 2>&1; then
        echo "❌ npm is required but not installed."
        echo "Please install npm (usually comes with Node.js)"
        exit 1
    fi

    echo "✅ Node.js $(node --version) and npm $(npm --version) are available"
}

# Check if no arguments provided
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

# Check requirements
check_requirements

# Process command
case "$1" in
    install)
        install_deps
        ;;
    dev)
        install_deps
        start_dev
        ;;
    build)
        install_deps
        build_prod
        ;;
    preview)
        preview_build
        ;;
    test)
        run_tests
        ;;
    lint)
        run_lint
        ;;
    clean)
        clean_build
        ;;
    help)
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac

echo ""
echo "🎉 Operation completed successfully!"
