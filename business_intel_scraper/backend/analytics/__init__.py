"""Analytics and Business Intelligence Dashboard Module.

This module provides comprehensive analytics capabilities including:
- Performance metrics tracking
- Data quality assessment
- System health monitoring
- Business intelligence insights
- Real-time analytics dashboard
"""

from .core import AnalyticsEngine
from .metrics import MetricsCollector
from .insights import InsightsGenerator
from .dashboard import DashboardAnalytics

__all__ = [
    "AnalyticsEngine",
    "MetricsCollector", 
    "InsightsGenerator",
    "DashboardAnalytics",
]
