"""
Advanced Crawling/Discovery Layer

This package implements the detailed best-practice pipeline for business intelligence
crawling with the following components:

- AdvancedCrawlManager: Comprehensive crawling system with intelligence and efficiency
- CrawlOrchestrator: High-level orchestrator for crawling operations  
- EnhancedAdaptiveLinkClassifier: Enhanced link classification with business patterns
- DiscoveredPage: Data structure for discovered page metadata
- SeedSource: Configuration for seed sources

Key Features:
- Seed-based crawling with known business sources
- Recursive crawling with depth control
- Domain and pattern-based scoping
- Metadata extraction and classification
- Duplicate avoidance with content hashing
- Robots.txt compliance
- Rate limiting and politeness
- Comprehensive metrics and monitoring
"""

from .advanced_crawler import AdvancedCrawlManager, DiscoveredPage, SeedSource
from .orchestrator import CrawlOrchestrator, EnhancedAdaptiveLinkClassifier

__all__ = [
    'AdvancedCrawlManager',
    'CrawlOrchestrator', 
    'EnhancedAdaptiveLinkClassifier',
    'DiscoveredPage',
    'SeedSource'
]

__version__ = '1.0.0'
