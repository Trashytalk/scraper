# ML Pipeline Package
# Advanced Analytics & AI Integration - Phase 4

"""
Business Intelligence Scraper - ML Pipeline Package

This package provides advanced machine learning and AI capabilities including:
- Content analysis and clustering
- Predictive analytics and trend detection  
- Real-time analytics and monitoring
- AI-powered insights and recommendations
- Advanced data visualizations

Components:
- ai_analytics: Core ML analysis and clustering
- realtime_analytics: Real-time monitoring and alerting
- visualization_engine: Advanced chart generation
- ai_integration_service: Main orchestration service
"""

from .ai_analytics import (
    MLDataProcessor,
    ContentClusteringEngine,
    PredictiveAnalytics,
    AIInsightsGenerator
)

from .realtime_analytics import (
    RealTimeMetric,
    AnalyticsEvent,
    MetricsCollector,
    RealTimeAnalyzer,
    AlertSystem,
    RealTimeAnalyticsEngine
)

from .visualization_engine import (
    ChartGenerator,
    InteractiveChartGenerator,
    AIInsightVisualizer
)

from .ai_integration_service import (
    AIIntegrationService,
    AnalysisRequest,
    AnalysisResult,
    ai_service
)

__version__ = "1.0.0"
__author__ = "Business Intelligence Scraper Team"

# Package-level convenience functions
def create_ai_service(config=None):
    """Create and configure AI integration service"""
    return AIIntegrationService(config)

def get_default_ai_service():
    """Get the default global AI service instance"""
    return ai_service

# Export all main classes and functions
__all__ = [
    # Core AI Analytics
    'MLDataProcessor',
    'ContentClusteringEngine', 
    'PredictiveAnalytics',
    'AIInsightsGenerator',
    
    # Real-time Analytics
    'RealTimeMetric',
    'AnalyticsEvent',
    'MetricsCollector',
    'RealTimeAnalyzer',
    'AlertSystem',
    'RealTimeAnalyticsEngine',
    
    # Visualization
    'ChartGenerator',
    'InteractiveChartGenerator',
    'AIInsightVisualizer',
    
    # Integration Service
    'AIIntegrationService',
    'AnalysisRequest',
    'AnalysisResult',
    'ai_service',
    
    # Convenience functions
    'create_ai_service',
    'get_default_ai_service'
]
