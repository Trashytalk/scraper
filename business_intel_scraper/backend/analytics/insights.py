"""Business Intelligence Insights Generator.

Generates actionable insights from collected analytics data including:
- Performance optimization recommendations
- Data quality improvement suggestions
- Capacity planning insights
- Anomaly detection and alerts
"""

from __future__ import annotations

import statistics
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .core import analytics_engine, PerformanceMetrics, DataQualityMetrics


class InsightsGenerator:
    """Generate actionable business intelligence insights."""
    
    def __init__(self) -> None:
        self.anomaly_threshold = 2.0  # Standard deviations for anomaly detection
        self.performance_baseline = None
        self.quality_baseline = None
    
    async def generate_performance_insights(self, 
                                          current_metrics: PerformanceMetrics) -> List[Dict[str, Any]]:
        """Generate performance optimization insights."""
        insights = []
        
        # Response time analysis
        if current_metrics.avg_response_time > 2.0:
            severity = "high" if current_metrics.avg_response_time > 5.0 else "medium"
            insights.append({
                "type": "performance",
                "severity": severity,
                "title": "Slow Response Times Detected",
                "description": f"Average response time is {current_metrics.avg_response_time:.2f}s",
                "recommendation": "Consider optimizing database queries, adding caching, or scaling resources",
                "impact": "User experience degradation",
                "metric_value": current_metrics.avg_response_time,
                "threshold": 2.0
            })
        
        # Error rate analysis
        if current_metrics.error_rate > 0.05:  # 5% error rate
            severity = "high" if current_metrics.error_rate > 0.1 else "medium"
            insights.append({
                "type": "reliability",
                "severity": severity,
                "title": "High Error Rate",
                "description": f"Error rate is {current_metrics.error_rate:.1%}",
                "recommendation": "Review error logs, check external dependencies, implement retry logic",
                "impact": "Service reliability issues",
                "metric_value": current_metrics.error_rate,
                "threshold": 0.05
            })
        
        # Throughput analysis
        if current_metrics.throughput < 10:  # Less than 10 requests/second
            insights.append({
                "type": "capacity",
                "severity": "low",
                "title": "Low System Throughput", 
                "description": f"Current throughput: {current_metrics.throughput:.1f} requests/second",
                "recommendation": "Monitor for capacity planning, consider horizontal scaling if demand increases",
                "impact": "May indicate underutilization or low demand",
                "metric_value": current_metrics.throughput,
                "threshold": 10
            })
        
        # Success rate analysis
        if current_metrics.success_rate < 0.95:  # Less than 95% success
            insights.append({
                "type": "reliability",
                "severity": "medium",
                "title": "Sub-optimal Success Rate",
                "description": f"Success rate: {current_metrics.success_rate:.1%}",
                "recommendation": "Investigate failing requests, improve error handling, check service dependencies",
                "impact": "Reduced system reliability",
                "metric_value": current_metrics.success_rate,
                "threshold": 0.95
            })
        
        return insights
    
    async def generate_quality_insights(self, 
                                      current_metrics: DataQualityMetrics) -> List[Dict[str, Any]]:
        """Generate data quality improvement insights."""
        insights = []
        
        # Overall quality score
        if current_metrics.quality_score < 0.8:  # Less than 80% quality
            severity = "high" if current_metrics.quality_score < 0.6 else "medium"
            insights.append({
                "type": "data_quality",
                "severity": severity,
                "title": "Poor Data Quality Detected",
                "description": f"Overall quality score: {current_metrics.quality_score:.1%}",
                "recommendation": "Review data validation rules, improve source data quality, implement data cleansing",
                "impact": "Unreliable analysis and reporting",
                "metric_value": current_metrics.quality_score,
                "threshold": 0.8
            })
        
        # Completeness analysis
        if current_metrics.completeness_rate < 0.9:  # Less than 90% complete
            insights.append({
                "type": "data_completeness",
                "severity": "medium",
                "title": "Data Completeness Issues",
                "description": f"Completeness rate: {current_metrics.completeness_rate:.1%}",
                "recommendation": "Improve data collection processes, add required field validation",
                "impact": "Incomplete analysis results",
                "metric_value": current_metrics.completeness_rate,
                "threshold": 0.9
            })
        
        # Duplicate analysis
        duplicate_rate = current_metrics.duplicate_records / current_metrics.total_records if current_metrics.total_records > 0 else 0
        if duplicate_rate > 0.1:  # More than 10% duplicates
            insights.append({
                "type": "data_duplicates",
                "severity": "medium",
                "title": "High Duplicate Rate",
                "description": f"Duplicate rate: {duplicate_rate:.1%} ({current_metrics.duplicate_records} records)",
                "recommendation": "Implement deduplication logic, review data ingestion process",
                "impact": "Inflated metrics and wasted storage",
                "metric_value": duplicate_rate,
                "threshold": 0.1
            })
        
        # Accuracy analysis  
        if current_metrics.accuracy_rate < 0.95:  # Less than 95% accurate
            insights.append({
                "type": "data_accuracy",
                "severity": "medium",
                "title": "Data Accuracy Concerns",
                "description": f"Accuracy rate: {current_metrics.accuracy_rate:.1%}",
                "recommendation": "Enhance data validation, improve source reliability, add quality checks",
                "impact": "Incorrect analysis and decisions",
                "metric_value": current_metrics.accuracy_rate,
                "threshold": 0.95
            })
        
        return insights
    
    async def detect_anomalies(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Detect anomalies in system behavior."""
        anomalies: List[Dict[str, Any]] = []
        
        # Get historical data
        response_time_data = await analytics_engine.get_historical_data("api.request", hours)
        
        if len(response_time_data) < 10:  # Need sufficient data
            return anomalies
        
        # Analyze response time anomalies
        response_times = [point["value"] for point in response_time_data]
        mean_time = statistics.mean(response_times)
        stdev_time = statistics.stdev(response_times) if len(response_times) > 1 else 0
        
        if stdev_time > 0:
            for i, time_point in enumerate(response_time_data[-10:]):  # Check last 10 points
                z_score = abs((time_point["value"] - mean_time) / stdev_time)
                if z_score > self.anomaly_threshold:
                    anomalies.append({
                        "type": "anomaly",
                        "severity": "high" if z_score > 3.0 else "medium",
                        "title": "Response Time Anomaly",
                        "description": f"Unusual response time: {time_point['value']:.2f}s (z-score: {z_score:.1f})",
                        "timestamp": time_point["timestamp"],
                        "recommendation": "Investigate system load, check for performance bottlenecks",
                        "metric_value": time_point["value"],
                        "baseline": mean_time,
                        "z_score": z_score
                    })
        
        return anomalies
    
    async def generate_capacity_insights(self) -> List[Dict[str, Any]]:
        """Generate capacity planning insights."""
        insights = []
        
        # Get historical system metrics
        cpu_data = await analytics_engine.get_historical_data("system.cpu_percent", 24)
        memory_data = await analytics_engine.get_historical_data("system.memory_percent", 24)
        
        # CPU analysis
        if cpu_data:
            recent_cpu = [point["value"] for point in cpu_data[-12:]]  # Last 12 points
            avg_cpu = statistics.mean(recent_cpu)
            
            if avg_cpu > 80:
                insights.append({
                    "type": "capacity",
                    "severity": "high",
                    "title": "High CPU Usage",
                    "description": f"Average CPU usage: {avg_cpu:.1f}%",
                    "recommendation": "Scale CPU resources or optimize application performance",
                    "impact": "Performance degradation risk",
                    "metric_value": avg_cpu,
                    "threshold": 80
                })
            elif avg_cpu > 60:
                insights.append({
                    "type": "capacity",
                    "severity": "medium",
                    "title": "Elevated CPU Usage",
                    "description": f"Average CPU usage: {avg_cpu:.1f}%",
                    "recommendation": "Monitor CPU trends, prepare for scaling",
                    "impact": "Approaching capacity limits",
                    "metric_value": avg_cpu,
                    "threshold": 60
                })
        
        # Memory analysis
        if memory_data:
            recent_memory = [point["value"] for point in memory_data[-12:]]
            avg_memory = statistics.mean(recent_memory)
            
            if avg_memory > 85:
                insights.append({
                    "type": "capacity",
                    "severity": "high",
                    "title": "High Memory Usage",
                    "description": f"Average memory usage: {avg_memory:.1f}%",
                    "recommendation": "Scale memory resources or optimize memory usage",
                    "impact": "Risk of out-of-memory errors",
                    "metric_value": avg_memory,
                    "threshold": 85
                })
        
        return insights
    
    async def generate_optimization_suggestions(self) -> List[Dict[str, Any]]:
        """Generate system optimization suggestions."""
        suggestions = []
        
        # Get current performance metrics
        performance = analytics_engine.get_performance_metrics()
        
        # Database optimization suggestions
        if performance.avg_response_time > 1.0:
            suggestions.append({
                "type": "optimization",
                "category": "database",
                "title": "Database Query Optimization",
                "description": "Response times suggest database queries may be slow",
                "recommendations": [
                    "Add database indexes on frequently queried columns",
                    "Optimize slow queries identified in logs",
                    "Consider database connection pooling",
                    "Implement query result caching"
                ],
                "impact": "Significant response time improvement",
                "effort": "medium"
            })
        
        # Caching suggestions
        if performance.request_count > 100 and performance.avg_response_time > 0.5:
            suggestions.append({
                "type": "optimization", 
                "category": "caching",
                "title": "Implement Response Caching",
                "description": "High request volume with slow responses indicates caching opportunity",
                "recommendations": [
                    "Implement Redis caching for frequent queries",
                    "Add HTTP response caching headers",
                    "Cache computed results and aggregations",
                    "Use CDN for static assets"
                ],
                "impact": "Major performance improvement",
                "effort": "medium"
            })
        
        # Monitoring suggestions
        suggestions.append({
            "type": "optimization",
            "category": "monitoring",
            "title": "Enhanced Monitoring",
            "description": "Improve observability and alerting",
            "recommendations": [
                "Set up automated alerts for key metrics",
                "Implement distributed tracing",
                "Add custom business metrics",
                "Create operational dashboards"
            ],
            "impact": "Better system visibility",
            "effort": "low"
        })
        
        return suggestions
    
    async def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive analytics insights report."""
        # Get current metrics
        performance = analytics_engine.get_performance_metrics()
        
        # Generate insights
        performance_insights = await self.generate_performance_insights(performance)
        anomalies = await self.detect_anomalies()
        capacity_insights = await self.generate_capacity_insights()
        optimization_suggestions = await self.generate_optimization_suggestions()
        
        # Get analytics summary
        analytics_summary = await analytics_engine.get_analytics_summary()
        
        # Calculate overall system health score
        health_score = self._calculate_health_score(performance, analytics_summary)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "health_score": health_score,
            "summary": analytics_summary,
            "insights": {
                "performance": performance_insights,
                "anomalies": anomalies,
                "capacity": capacity_insights,
                "optimization": optimization_suggestions
            },
            "recommendations": self._prioritize_recommendations(
                performance_insights + anomalies + capacity_insights
            ),
            "metrics_summary": {
                "performance": performance.to_dict(),
                "data_quality": analytics_summary.get("data_quality", {}),
                "trends": analytics_summary.get("trends", {})
            }
        }
    
    def _calculate_health_score(self, performance: PerformanceMetrics, 
                              analytics_summary: Dict[str, Any]) -> float:
        """Calculate overall system health score (0-100)."""
        score = 100.0
        
        # Performance factors
        if performance.error_rate > 0.05:
            score -= min(30, performance.error_rate * 500)  # Cap at 30 points
        
        if performance.avg_response_time > 2.0:
            score -= min(20, (performance.avg_response_time - 2.0) * 10)
        
        # Data quality factors
        quality = analytics_summary.get("data_quality", {})
        quality_score = quality.get("quality_score", 1.0)
        if quality_score < 0.8:
            score -= (0.8 - quality_score) * 100
        
        # Ensure score stays within bounds
        return max(0.0, min(100.0, score))
    
    def _prioritize_recommendations(self, insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize recommendations by severity and impact."""
        # Sort by severity (high -> medium -> low) then by impact
        severity_order = {"high": 3, "medium": 2, "low": 1}
        
        sorted_insights = sorted(
            insights,
            key=lambda x: (
                severity_order.get(x.get("severity", "low"), 1),
                len(x.get("recommendation", ""))  # Longer recommendations assumed more important
            ),
            reverse=True
        )
        
        return sorted_insights[:10]  # Return top 10 recommendations


# Global insights generator instance
insights_generator = InsightsGenerator()
