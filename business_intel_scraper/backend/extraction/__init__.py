"""
Adaptive Extraction Engine for Business Intelligence Scraper

This module implements adaptive schema detection and extraction capabilities
using machine learning to automatically identify and extract structured data.
"""

from .adaptive_scraper import AdaptiveBusinessScraper
from .schema_detector import SchemaDetector
from .template_manager import TemplateManager

__all__ = [
    'AdaptiveBusinessScraper',
    'SchemaDetector', 
    'TemplateManager'
]
