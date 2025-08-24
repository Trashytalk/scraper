"""
CFPL Storage Module
Capture-First, Process-Later implementation for web scraping
"""

from .cas_store import CASStore
from .capture_engine import CFPLCaptureEngine, capture_single_url
from .config import CFPLConfig, CFPLConfigManager, get_config
from .processors import ProcessingPipeline, HTMLProcessor, TextExtractor, MediaMetadataProcessor
from .cfpl_integration import CFPLScrapingEngine, create_scraping_engine, get_cfpl_scraping_engine

__version__ = "1.0.0"

__all__ = [
    "CASStore",
    "CFPLCaptureEngine", 
    "capture_single_url",
    "CFPLConfig",
    "CFPLConfigManager", 
    "get_config",
    "ProcessingPipeline",
    "HTMLProcessor",
    "TextExtractor", 
    "MediaMetadataProcessor",
    "CFPLScrapingEngine",
    "create_scraping_engine",
    "get_cfpl_scraping_engine"
]
