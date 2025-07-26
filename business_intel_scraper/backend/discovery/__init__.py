"""
Intelligent Discovery Engine for Business Intelligence Scraper

This module implements ML-powered crawling intelligence and automated source discovery including:
- IntelligentCrawlScheduler with priority-based queue management
- AdaptiveLinkClassifier using RandomForest for link categorization
- NetworkX-based crawl graph analysis and optimization
- AutomatedDiscoveryManager for intelligent source discovery
- Multi-bot discovery system with specialized strategies
- Marketplace integration for automatic spider generation

Phase 1 Implementation (COMPLETED):
- Core Automated Discovery with multi-bot strategies
- Source registry with persistence and confidence scoring
- Celery task integration for scheduled discovery
- CLI tools and marketplace integration

Usage:
    # Automated Discovery
    from .automated_discovery import AutomatedDiscoveryManager
    manager = AutomatedDiscoveryManager()
    sources = await manager.discover_sources(['https://example.com'])

    # Intelligent Crawling
    from .scheduler import IntelligentCrawlScheduler
    scheduler = IntelligentCrawlScheduler()
"""

from .scheduler import IntelligentCrawlScheduler

# Automated Discovery System (Phase 1)
try:
    from .automated_discovery import (
        AutomatedDiscoveryManager,
        DiscoveredSource,
        SourceDiscoveryBot,
        DomainScannerBot,
        SearchEngineBot,
        HeuristicAnalyzerBot,
        SourceRegistry,
    )
    from .marketplace_integration import MarketplaceIntegration

    __all__ = [
        "IntelligentCrawlScheduler",
        "AutomatedDiscoveryManager",
        "DiscoveredSource",
        "SourceDiscoveryBot",
        "DomainScannerBot",
        "SearchEngineBot",
        "HeuristicAnalyzerBot",
        "SourceRegistry",
        "MarketplaceIntegration",
    ]
except ImportError:
    # Automated discovery not available
    __all__ = ["IntelligentCrawlScheduler"]
from .classifier import AdaptiveLinkClassifier
from .graph_analyzer import CrawlGraphAnalyzer

__all__ = ["IntelligentCrawlScheduler", "AdaptiveLinkClassifier", "CrawlGraphAnalyzer"]
