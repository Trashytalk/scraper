"""
Intelligent Crawl Scheduler with ML-Powered Priority Management

This module implements the IntelligentCrawlScheduler from the advanced guide,
providing adaptive crawling with machine learning-based URL prioritization.
"""

import asyncio
import logging
import time
from collections import defaultdict, deque
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import pickle
from pathlib import Path

try:
    import networkx as nx
    import numpy as np
    import pandas as pd
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    nx = None
    np = None
    pd = None

logger = logging.getLogger(__name__)


class CrawlPriority(Enum):
    """Priority levels for crawl scheduling"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


@dataclass
class CrawlRequest:
    """Represents a crawl request with metadata"""
    url: str
    spider_name: str
    priority: CrawlPriority = CrawlPriority.NORMAL
    depth: int = 0
    parent_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    estimated_value: float = 0.0
    retry_count: int = 0
    max_retries: int = 3
    
    def __post_init__(self):
        if isinstance(self.priority, str):
            self.priority = CrawlPriority[self.priority.upper()]


@dataclass
class CrawlStats:
    """Statistics for crawl performance tracking"""
    total_requests: int = 0
    completed_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    success_rate: float = 0.0
    data_quality_score: float = 0.0
    last_updated: float = field(default_factory=time.time)


class IntelligentCrawlScheduler:
    """
    ML-powered crawl scheduler with adaptive priority management.
    
    Features:
    - Priority-based queue management with ML scoring
    - NetworkX graph analysis for crawl optimization
    - Adaptive learning from crawl success patterns
    - Resource-aware scheduling and throttling
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.priority_queues: Dict[CrawlPriority, deque] = {
            priority: deque() for priority in CrawlPriority
        }
        self.crawl_graph: Optional[Any] = nx.DiGraph() if nx else None
        self.url_stats: Dict[str, CrawlStats] = {}
        self.domain_stats: Dict[str, CrawlStats] = {}
        self.active_crawls: Dict[str, CrawlRequest] = {}
        self.completed_crawls: List[CrawlRequest] = []
        
        # ML components
        self.priority_model: Optional[Any] = None
        self.feature_scaler: Optional[Any] = None
        self.is_trained = False
        
        # Configuration
        self.max_concurrent_crawls = self.config.get('max_concurrent_crawls', 10)
        self.max_queue_size = self.config.get('max_queue_size', 10000)
        self.enable_ml_scoring = self.config.get('enable_ml_scoring', True) and SKLEARN_AVAILABLE
        self.model_update_interval = self.config.get('model_update_interval', 1000)  # requests
        
        # Performance tracking
        self.requests_processed = 0
        self.last_model_update = 0
        
        logger.info(f"IntelligentCrawlScheduler initialized with ML support: {self.enable_ml_scoring}")
        
        if self.enable_ml_scoring:
            self._initialize_ml_components()
    
    def _initialize_ml_components(self) -> None:
        """Initialize machine learning components"""
        if not SKLEARN_AVAILABLE:
            logger.warning("scikit-learn not available, disabling ML features")
            self.enable_ml_scoring = False
            return
            
        self.priority_model = RandomForestRegressor(
            n_estimators=100,
            random_state=42,
            n_jobs=-1
        )
        self.feature_scaler = StandardScaler()
        
        # Try to load existing model
        model_path = Path(self.config.get('model_path', 'data/models/crawl_scheduler.pkl'))
        if model_path.exists():
            self._load_model(model_path)
    
    def add_crawl_request(self, request: CrawlRequest) -> bool:
        """Add a crawl request to the appropriate priority queue"""
        try:
            # Check queue size limits
            total_queued = sum(len(queue) for queue in self.priority_queues.values())
            if total_queued >= self.max_queue_size:
                logger.warning("Crawl queue is full, dropping request")
                return False
            
            # Update priority with ML scoring if enabled
            if self.enable_ml_scoring and self.is_trained:
                request.estimated_value = self._calculate_ml_priority(request)
                request.priority = self._value_to_priority(request.estimated_value)
            
            # Add to graph if enabled
            if self.crawl_graph is not None:
                self._update_crawl_graph(request)
            
            # Add to appropriate queue
            self.priority_queues[request.priority].append(request)
            logger.debug(f"Added crawl request: {request.url} (priority: {request.priority.name})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add crawl request: {e}")
            return False
    
    def get_next_crawl_request(self) -> Optional[CrawlRequest]:
        """Get the next highest priority crawl request"""
        # Check concurrent crawl limits
        if len(self.active_crawls) >= self.max_concurrent_crawls:
            return None
        
        # Get request from highest priority non-empty queue
        for priority in CrawlPriority:
            queue = self.priority_queues[priority]
            if queue:
                request = queue.popleft()
                self.active_crawls[request.url] = request
                logger.debug(f"Dispatched crawl request: {request.url}")
                return request
        
        return None
    
    def complete_crawl_request(
        self, 
        url: str, 
        success: bool, 
        response_time: float = 0.0,
        data_quality: float = 0.0,
        extracted_links: Optional[List[str]] = None
    ) -> None:
        """Mark a crawl request as completed and update statistics"""
        if url not in self.active_crawls:
            logger.warning(f"Completing unknown crawl request: {url}")
            return
        
        request = self.active_crawls.pop(url)
        request.metadata.update({
            'completed_at': time.time(),
            'success': success,
            'response_time': response_time,
            'data_quality': data_quality
        })
        
        self.completed_crawls.append(request)
        self.requests_processed += 1
        
        # Update statistics
        self._update_crawl_stats(request, success, response_time, data_quality)
        
        # Add extracted links to graph
        if extracted_links and self.crawl_graph is not None:
            self._add_extracted_links(url, extracted_links)
        
        # Periodic model updates
        if (self.enable_ml_scoring and 
            self.requests_processed - self.last_model_update >= self.model_update_interval):
            self._update_ml_model()
        
        logger.debug(f"Completed crawl request: {url} (success: {success})")
    
    def fail_crawl_request(self, url: str, error: str) -> None:
        """Handle failed crawl request with retry logic"""
        if url not in self.active_crawls:
            logger.warning(f"Failing unknown crawl request: {url}")
            return
        
        request = self.active_crawls.pop(url)
        request.retry_count += 1
        
        if request.retry_count <= request.max_retries:
            # Retry with lower priority
            request.priority = CrawlPriority.LOW
            self.priority_queues[request.priority].append(request)
            logger.info(f"Retrying crawl request: {url} (attempt {request.retry_count})")
        else:
            # Mark as permanently failed
            request.metadata.update({
                'completed_at': time.time(),
                'success': False,
                'error': error
            })
            self.completed_crawls.append(request)
            logger.warning(f"Permanently failed crawl request: {url} after {request.retry_count} attempts")
    
    def _calculate_ml_priority(self, request: CrawlRequest) -> float:
        """Calculate priority score using ML model"""
        if not self.is_trained:
            return 0.5  # neutral priority
        
        features = self._extract_features(request)
        if features is None:
            return 0.5
        
        try:
            features_scaled = self.feature_scaler.transform([features])
            priority_score = self.priority_model.predict(features_scaled)[0]
            return max(0.0, min(1.0, priority_score))  # clamp to [0,1]
        except Exception as e:
            logger.error(f"ML priority calculation failed: {e}")
            return 0.5
    
    def _extract_features(self, request: CrawlRequest) -> Optional[List[float]]:
        """Extract features for ML priority scoring"""
        try:
            from urllib.parse import urlparse
            
            parsed_url = urlparse(request.url)
            domain = parsed_url.netloc
            
            # Basic features
            features = [
                request.depth,
                len(request.url),
                len(parsed_url.path.split('/')),
                1.0 if parsed_url.path.endswith('.html') else 0.0,
                1.0 if 'news' in request.url.lower() else 0.0,
                1.0 if 'product' in request.url.lower() else 0.0,
            ]
            
            # Domain statistics
            if domain in self.domain_stats:
                stats = self.domain_stats[domain]
                features.extend([
                    stats.success_rate,
                    stats.avg_response_time,
                    stats.data_quality_score
                ])
            else:
                features.extend([0.5, 1.0, 0.5])  # default values
            
            # Graph-based features
            if self.crawl_graph and request.url in self.crawl_graph:
                try:
                    features.extend([
                        self.crawl_graph.in_degree(request.url),
                        self.crawl_graph.out_degree(request.url),
                        nx.pagerank(self.crawl_graph).get(request.url, 0.0)
                    ])
                except:
                    features.extend([0.0, 0.0, 0.0])
            else:
                features.extend([0.0, 0.0, 0.0])
            
            return features
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return None
    
    def _value_to_priority(self, value: float) -> CrawlPriority:
        """Convert ML priority value to CrawlPriority enum"""
        if value >= 0.8:
            return CrawlPriority.CRITICAL
        elif value >= 0.6:
            return CrawlPriority.HIGH
        elif value >= 0.4:
            return CrawlPriority.NORMAL
        elif value >= 0.2:
            return CrawlPriority.LOW
        else:
            return CrawlPriority.BACKGROUND
    
    def _update_crawl_graph(self, request: CrawlRequest) -> None:
        """Update the crawl graph with new request"""
        if not self.crawl_graph:
            return
        
        try:
            self.crawl_graph.add_node(request.url, **request.metadata)
            
            if request.parent_url:
                self.crawl_graph.add_edge(
                    request.parent_url, 
                    request.url,
                    depth=request.depth
                )
        except Exception as e:
            logger.error(f"Failed to update crawl graph: {e}")
    
    def _add_extracted_links(self, parent_url: str, links: List[str]) -> None:
        """Add extracted links to the crawl graph"""
        if not self.crawl_graph:
            return
        
        try:
            for link in links:
                self.crawl_graph.add_node(link)
                self.crawl_graph.add_edge(parent_url, link, extracted=True)
        except Exception as e:
            logger.error(f"Failed to add extracted links: {e}")
    
    def _update_crawl_stats(
        self, 
        request: CrawlRequest, 
        success: bool, 
        response_time: float,
        data_quality: float
    ) -> None:
        """Update crawl statistics for learning"""
        from urllib.parse import urlparse
        
        domain = urlparse(request.url).netloc
        
        # Update URL stats
        if request.url not in self.url_stats:
            self.url_stats[request.url] = CrawlStats()
        
        url_stats = self.url_stats[request.url]
        url_stats.total_requests += 1
        if success:
            url_stats.completed_requests += 1
        else:
            url_stats.failed_requests += 1
        
        # Update moving averages
        url_stats.avg_response_time = (
            (url_stats.avg_response_time * (url_stats.total_requests - 1) + response_time) / 
            url_stats.total_requests
        )
        url_stats.success_rate = url_stats.completed_requests / url_stats.total_requests
        url_stats.data_quality_score = (
            (url_stats.data_quality_score * (url_stats.total_requests - 1) + data_quality) /
            url_stats.total_requests
        )
        url_stats.last_updated = time.time()
        
        # Update domain stats
        if domain not in self.domain_stats:
            self.domain_stats[domain] = CrawlStats()
        
        domain_stats = self.domain_stats[domain]
        domain_stats.total_requests += 1
        if success:
            domain_stats.completed_requests += 1
        else:
            domain_stats.failed_requests += 1
        
        domain_stats.avg_response_time = (
            (domain_stats.avg_response_time * (domain_stats.total_requests - 1) + response_time) /
            domain_stats.total_requests
        )
        domain_stats.success_rate = domain_stats.completed_requests / domain_stats.total_requests
        domain_stats.data_quality_score = (
            (domain_stats.data_quality_score * (domain_stats.total_requests - 1) + data_quality) /
            domain_stats.total_requests
        )
        domain_stats.last_updated = time.time()
    
    def _update_ml_model(self) -> None:
        """Update the ML model with recent crawl data"""
        if not self.enable_ml_scoring or len(self.completed_crawls) < 100:
            return
        
        try:
            # Prepare training data
            features = []
            targets = []
            
            for request in self.completed_crawls[-1000:]:  # use last 1000 requests
                feature_vector = self._extract_features(request)
                if feature_vector is None:
                    continue
                
                # Calculate target value based on success metrics
                success = request.metadata.get('success', False)
                response_time = request.metadata.get('response_time', 10.0)
                data_quality = request.metadata.get('data_quality', 0.0)
                
                target_value = 0.0
                if success:
                    target_value = 0.5  # base success score
                    target_value += 0.3 * data_quality  # quality bonus
                    target_value += max(0, 0.2 * (1.0 - min(response_time / 5.0, 1.0)))  # speed bonus
                
                features.append(feature_vector)
                targets.append(target_value)
            
            if len(features) < 50:  # minimum training data
                return
            
            # Train model
            X = np.array(features)
            y = np.array(targets)
            
            # Scale features
            X_scaled = self.feature_scaler.fit_transform(X)
            
            # Train/test split
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42
            )
            
            # Fit model
            self.priority_model.fit(X_train, y_train)
            
            # Evaluate
            train_score = self.priority_model.score(X_train, y_train)
            test_score = self.priority_model.score(X_test, y_test)
            
            self.is_trained = True
            self.last_model_update = self.requests_processed
            
            logger.info(f"Updated ML model - Train R²: {train_score:.3f}, Test R²: {test_score:.3f}")
            
            # Save model
            self._save_model()
            
        except Exception as e:
            logger.error(f"Failed to update ML model: {e}")
    
    def _save_model(self) -> None:
        """Save the trained ML model"""
        try:
            model_path = Path(self.config.get('model_path', 'data/models/crawl_scheduler.pkl'))
            model_path.parent.mkdir(parents=True, exist_ok=True)
            
            model_data = {
                'priority_model': self.priority_model,
                'feature_scaler': self.feature_scaler,
                'is_trained': self.is_trained,
                'last_update': time.time()
            }
            
            with open(model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"Saved ML model to {model_path}")
            
        except Exception as e:
            logger.error(f"Failed to save ML model: {e}")
    
    def _load_model(self, model_path: Path) -> None:
        """Load a saved ML model"""
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.priority_model = model_data['priority_model']
            self.feature_scaler = model_data['feature_scaler']
            self.is_trained = model_data.get('is_trained', False)
            
            logger.info(f"Loaded ML model from {model_path}")
            
        except Exception as e:
            logger.error(f"Failed to load ML model: {e}")
    
    def get_scheduler_stats(self) -> Dict[str, Any]:
        """Get comprehensive scheduler statistics"""
        total_queued = sum(len(queue) for queue in self.priority_queues.values())
        
        return {
            'active_crawls': len(self.active_crawls),
            'total_queued': total_queued,
            'completed_crawls': len(self.completed_crawls),
            'requests_processed': self.requests_processed,
            'ml_enabled': self.enable_ml_scoring,
            'ml_trained': self.is_trained,
            'queue_breakdown': {
                priority.name: len(queue) 
                for priority, queue in self.priority_queues.items()
            },
            'top_domains': {
                domain: {
                    'success_rate': stats.success_rate,
                    'avg_response_time': stats.avg_response_time,
                    'total_requests': stats.total_requests
                }
                for domain, stats in sorted(
                    self.domain_stats.items(),
                    key=lambda x: x[1].total_requests,
                    reverse=True
                )[:10]
            }
        }
    
    def optimize_crawl_strategy(self) -> Dict[str, Any]:
        """Analyze crawl patterns and suggest optimizations"""
        if not self.crawl_graph or not self.completed_crawls:
            return {"recommendations": ["Insufficient data for optimization"]}
        
        recommendations = []
        
        try:
            # Analyze graph structure
            if len(self.crawl_graph.nodes()) > 0:
                density = nx.density(self.crawl_graph)
                if density < 0.1:
                    recommendations.append("Low graph connectivity - consider broader discovery strategies")
                elif density > 0.8:
                    recommendations.append("High graph density - consider more selective crawling")
            
            # Analyze success patterns
            recent_requests = self.completed_crawls[-100:]
            success_rate = sum(1 for r in recent_requests if r.metadata.get('success', False)) / len(recent_requests)
            
            if success_rate < 0.8:
                recommendations.append("Low success rate - review target selection and retry policies")
            
            # Domain performance analysis
            if self.domain_stats:
                best_domains = sorted(
                    self.domain_stats.items(),
                    key=lambda x: x[1].success_rate * x[1].data_quality_score,
                    reverse=True
                )[:5]
                
                recommendations.append(f"Top performing domains: {[d[0] for d in best_domains]}")
            
            return {
                "recommendations": recommendations,
                "success_rate": success_rate,
                "graph_density": density if 'density' in locals() else 0.0
            }
            
        except Exception as e:
            logger.error(f"Optimization analysis failed: {e}")
            return {"recommendations": ["Analysis failed - check logs"]}
