# Real-time Analytics Engine
# Advanced Analytics & AI Integration - Phase 4

import asyncio
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
from collections import defaultdict, deque
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import time

logger = logging.getLogger(__name__)

@dataclass
class RealTimeMetric:
    """Real-time metric data structure"""
    timestamp: datetime
    metric_name: str
    value: float
    metadata: Dict[str, Any]
    source: str

@dataclass
class AnalyticsEvent:
    """Analytics event data structure"""
    event_id: str
    event_type: str
    timestamp: datetime
    data: Dict[str, Any]
    session_id: Optional[str] = None

class MetricsCollector:
    """Collects and aggregates real-time metrics"""
    
    def __init__(self, max_history: int = 1000):
        self.metrics_history = deque(maxlen=max_history)
        self.current_metrics = {}
        self.aggregators = {
            'content_quality': deque(maxlen=100),
            'scraping_speed': deque(maxlen=100),
            'error_rate': deque(maxlen=100),
            'data_volume': deque(maxlen=100)
        }
        
    def record_metric(self, name: str, value: float, metadata: Dict[str, Any] = None, source: str = "system"):
        """Record a new metric value"""
        metric = RealTimeMetric(
            timestamp=datetime.now(),
            metric_name=name,
            value=value,
            metadata=metadata or {},
            source=source
        )
        
        self.metrics_history.append(metric)
        self.current_metrics[name] = metric
        
        # Update aggregators
        if name in self.aggregators:
            self.aggregators[name].append(value)
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current metric values"""
        return {
            name: {
                'value': metric.value,
                'timestamp': metric.timestamp.isoformat(),
                'metadata': metric.metadata
            }
            for name, metric in self.current_metrics.items()
        }
    
    def get_metric_trend(self, metric_name: str, duration_minutes: int = 60) -> Dict[str, Any]:
        """Get trend data for a specific metric"""
        cutoff_time = datetime.now() - timedelta(minutes=duration_minutes)
        
        trend_data = [
            metric for metric in self.metrics_history
            if metric.metric_name == metric_name and metric.timestamp >= cutoff_time
        ]
        
        if not trend_data:
            return {}
        
        values = [m.value for m in trend_data]
        timestamps = [m.timestamp.isoformat() for m in trend_data]
        
        return {
            'values': values,
            'timestamps': timestamps,
            'avg': np.mean(values),
            'min': np.min(values),
            'max': np.max(values),
            'trend': 'increasing' if values[-1] > values[0] else 'decreasing' if values[-1] < values[0] else 'stable'
        }

class RealTimeAnalyzer:
    """Real-time data analysis and pattern detection"""
    
    def __init__(self):
        self.data_buffer = deque(maxlen=500)
        self.analysis_cache = {}
        self.last_analysis = datetime.now()
        
    def add_data_point(self, data: Dict[str, Any]):
        """Add new data point for real-time analysis"""
        enriched_data = {
            **data,
            'timestamp': datetime.now().isoformat(),
            'analysis_id': f"rt_{int(time.time() * 1000)}"
        }
        self.data_buffer.append(enriched_data)
    
    def analyze_real_time_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in real-time data"""
        if not self.data_buffer:
            return {}
        
        try:
            # Convert to DataFrame for analysis
            df = pd.DataFrame(list(self.data_buffer))
            
            # Real-time statistics
            stats = self._calculate_real_time_stats(df)
            
            # Pattern detection
            patterns = self._detect_patterns(df)
            
            # Velocity analysis
            velocity = self._analyze_data_velocity()
            
            # Quality monitoring
            quality = self._monitor_quality(df)
            
            analysis_result = {
                'statistics': stats,
                'patterns': patterns,
                'velocity': velocity,
                'quality': quality,
                'data_points': len(self.data_buffer),
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            self.analysis_cache = analysis_result
            self.last_analysis = datetime.now()
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error in real-time analysis: {e}")
            return {}
    
    def _calculate_real_time_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate real-time statistics"""
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        stats = {}
        for col in numeric_columns:
            if len(df[col]) > 0:
                stats[col] = {
                    'mean': float(df[col].mean()),
                    'std': float(df[col].std()) if len(df[col]) > 1 else 0.0,
                    'min': float(df[col].min()),
                    'max': float(df[col].max()),
                    'recent_value': float(df[col].iloc[-1]) if len(df[col]) > 0 else 0.0
                }
        
        return stats
    
    def _detect_patterns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect patterns in real-time data"""
        patterns = []
        
        # Data volume pattern
        recent_data = df.tail(10)
        if len(recent_data) >= 5:
            data_rate = len(recent_data) / 5  # items per minute (assuming 5-minute window)
            
            if data_rate > 10:
                patterns.append({
                    'type': 'high_volume',
                    'description': f'High data ingestion rate: {data_rate:.1f} items/min',
                    'severity': 'info'
                })
            elif data_rate < 1:
                patterns.append({
                    'type': 'low_volume',
                    'description': f'Low data ingestion rate: {data_rate:.1f} items/min',
                    'severity': 'warning'
                })
        
        # Quality degradation pattern
        if 'content_quality_score' in df.columns:
            recent_quality = df['content_quality_score'].tail(10).mean()
            overall_quality = df['content_quality_score'].mean()
            
            if recent_quality < overall_quality * 0.8:
                patterns.append({
                    'type': 'quality_degradation',
                    'description': f'Content quality dropping: {recent_quality:.2f} vs {overall_quality:.2f} avg',
                    'severity': 'warning'
                })
        
        return patterns
    
    def _analyze_data_velocity(self) -> Dict[str, Any]:
        """Analyze data ingestion velocity"""
        if len(self.data_buffer) < 2:
            return {}
        
        # Calculate time differences between data points
        timestamps = []
        for item in list(self.data_buffer)[-10:]:  # Last 10 items
            try:
                ts = datetime.fromisoformat(item['timestamp'].replace('Z', '+00:00'))
                timestamps.append(ts)
            except:
                continue
        
        if len(timestamps) < 2:
            return {}
        
        intervals = []
        for i in range(1, len(timestamps)):
            interval = (timestamps[i] - timestamps[i-1]).total_seconds()
            intervals.append(interval)
        
        return {
            'avg_interval_seconds': np.mean(intervals),
            'min_interval_seconds': np.min(intervals),
            'max_interval_seconds': np.max(intervals),
            'items_per_minute': 60 / np.mean(intervals) if np.mean(intervals) > 0 else 0,
            'velocity_trend': 'stable'  # Could be enhanced with trend analysis
        }
    
    def _monitor_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Monitor data quality in real-time"""
        quality_metrics = {}
        
        # Completeness check
        total_fields = len(df.columns)
        completeness_scores = []
        
        for _, row in df.iterrows():
            non_null_fields = sum(1 for val in row.values if pd.notna(val) and val != '')
            completeness = non_null_fields / total_fields
            completeness_scores.append(completeness)
        
        quality_metrics['completeness'] = {
            'avg_completeness': np.mean(completeness_scores),
            'min_completeness': np.min(completeness_scores),
            'recent_completeness': completeness_scores[-1] if completeness_scores else 0
        }
        
        # Content quality (if available)
        if 'content_quality_score' in df.columns:
            quality_metrics['content_quality'] = {
                'avg_score': float(df['content_quality_score'].mean()),
                'recent_score': float(df['content_quality_score'].iloc[-1]),
                'declining_quality': bool(df['content_quality_score'].tail(5).mean() < df['content_quality_score'].mean())
            }
        
        return quality_metrics

class AlertSystem:
    """Real-time alerting system"""
    
    def __init__(self):
        self.alert_rules = []
        self.active_alerts = {}
        self.alert_history = deque(maxlen=100)
        
    def add_alert_rule(self, rule: Dict[str, Any]):
        """Add a new alert rule"""
        self.alert_rules.append({
            'id': f"rule_{len(self.alert_rules)}",
            'created': datetime.now().isoformat(),
            **rule
        })
    
    def check_alerts(self, metrics: Dict[str, Any], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for alert conditions"""
        triggered_alerts = []
        
        for rule in self.alert_rules:
            try:
                if self._evaluate_rule(rule, metrics, analysis):
                    alert = {
                        'id': f"alert_{int(time.time() * 1000)}",
                        'rule_id': rule['id'],
                        'message': rule.get('message', 'Alert triggered'),
                        'severity': rule.get('severity', 'warning'),
                        'timestamp': datetime.now().isoformat(),
                        'data': {
                            'metrics': metrics,
                            'analysis_summary': analysis.get('statistics', {})
                        }
                    }
                    
                    triggered_alerts.append(alert)
                    self.active_alerts[alert['id']] = alert
                    self.alert_history.append(alert)
                    
            except Exception as e:
                logger.error(f"Error evaluating alert rule {rule.get('id', 'unknown')}: {e}")
        
        return triggered_alerts
    
    def _evaluate_rule(self, rule: Dict[str, Any], metrics: Dict[str, Any], analysis: Dict[str, Any]) -> bool:
        """Evaluate if an alert rule is triggered"""
        condition = rule.get('condition', {})
        metric_name = condition.get('metric')
        operator = condition.get('operator')
        threshold = condition.get('threshold')
        
        if not all([metric_name, operator, threshold is not None]):
            return False
        
        # Get metric value
        metric_value = None
        if metric_name in metrics:
            metric_value = metrics[metric_name].get('value')
        elif metric_name in analysis.get('statistics', {}):
            metric_value = analysis['statistics'][metric_name].get('recent_value')
        
        if metric_value is None:
            return False
        
        # Evaluate condition
        if operator == 'gt':
            return metric_value > threshold
        elif operator == 'lt':
            return metric_value < threshold
        elif operator == 'eq':
            return metric_value == threshold
        elif operator == 'gte':
            return metric_value >= threshold
        elif operator == 'lte':
            return metric_value <= threshold
        
        return False

class RealTimeAnalyticsEngine:
    """Main real-time analytics engine"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.analyzer = RealTimeAnalyzer()
        self.alert_system = AlertSystem()
        self.is_running = False
        self.analysis_interval = 30  # seconds
        
        # Setup default alert rules
        self._setup_default_alerts()
    
    def _setup_default_alerts(self):
        """Setup default alert rules"""
        default_rules = [
            {
                'name': 'Low Content Quality',
                'condition': {
                    'metric': 'content_quality_score',
                    'operator': 'lt',
                    'threshold': 0.3
                },
                'message': 'Content quality has dropped below acceptable levels',
                'severity': 'warning'
            },
            {
                'name': 'High Error Rate',
                'condition': {
                    'metric': 'error_rate',
                    'operator': 'gt',
                    'threshold': 0.1
                },
                'message': 'Error rate is higher than normal',
                'severity': 'critical'
            },
            {
                'name': 'Low Data Volume',
                'condition': {
                    'metric': 'data_volume',
                    'operator': 'lt',
                    'threshold': 1.0
                },
                'message': 'Data ingestion volume is below expected levels',
                'severity': 'info'
            }
        ]
        
        for rule in default_rules:
            self.alert_system.add_alert_rule(rule)
    
    async def start_monitoring(self):
        """Start real-time monitoring"""
        self.is_running = True
        logger.info("Real-time analytics engine started")
        
        while self.is_running:
            try:
                # Perform analysis
                analysis = self.analyzer.analyze_real_time_patterns()
                
                # Get current metrics
                metrics = self.metrics_collector.get_current_metrics()
                
                # Check for alerts
                alerts = self.alert_system.check_alerts(metrics, analysis)
                
                if alerts:
                    logger.info(f"Triggered {len(alerts)} alerts")
                
                # Wait for next analysis cycle
                await asyncio.sleep(self.analysis_interval)
                
            except Exception as e:
                logger.error(f"Error in real-time monitoring: {e}")
                await asyncio.sleep(5)
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.is_running = False
        logger.info("Real-time analytics engine stopped")
    
    def add_data_point(self, data: Dict[str, Any]):
        """Add data point for analysis"""
        self.analyzer.add_data_point(data)
        
        # Extract and record metrics
        if 'content_quality_score' in data:
            self.metrics_collector.record_metric('content_quality_score', data['content_quality_score'])
        
        if 'content_length' in data:
            self.metrics_collector.record_metric('content_length', data['content_length'])
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get real-time dashboard data"""
        return {
            'metrics': self.metrics_collector.get_current_metrics(),
            'analysis': self.analyzer.analysis_cache,
            'alerts': list(self.alert_system.active_alerts.values()),
            'alert_history': list(self.alert_system.alert_history)[-10:],  # Last 10 alerts
            'system_status': {
                'is_monitoring': self.is_running,
                'last_update': datetime.now().isoformat(),
                'data_points_analyzed': len(self.analyzer.data_buffer)
            }
        }

# Export main classes
__all__ = [
    'RealTimeMetric',
    'AnalyticsEvent',
    'MetricsCollector',
    'RealTimeAnalyzer',
    'AlertSystem',
    'RealTimeAnalyticsEngine'
]
