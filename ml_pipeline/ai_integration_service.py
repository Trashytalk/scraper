# AI Integration Service
# Main service that integrates all AI and analytics components

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import json

# Import our AI components
from .ai_analytics import AIInsightsGenerator, MLDataProcessor
from .realtime_analytics import RealTimeAnalyticsEngine
from .visualization_engine import AIInsightVisualizer

logger = logging.getLogger(__name__)

@dataclass
class AnalysisRequest:
    """Analysis request data structure"""
    request_id: str
    data: List[Dict[str, Any]]
    analysis_type: str  # 'full', 'clustering', 'trends', 'realtime'
    options: Dict[str, Any]
    timestamp: datetime

@dataclass
class AnalysisResult:
    """Analysis result data structure"""
    request_id: str
    insights: Dict[str, Any]
    visualizations: Dict[str, Any]
    recommendations: List[str]
    processing_time: float
    timestamp: datetime

class AIIntegrationService:
    """Main AI integration service orchestrating all analytics components"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Initialize AI components
        self.insights_generator = AIInsightsGenerator()
        self.realtime_engine = RealTimeAnalyticsEngine()
        self.visualizer = AIInsightVisualizer()
        self.data_processor = MLDataProcessor()
        
        # Service state
        self.is_running = False
        self.analysis_queue = asyncio.Queue()
        self.results_cache = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Performance tracking
        self.analysis_count = 0
        self.total_processing_time = 0
        
        logger.info("AI Integration Service initialized")
    
    async def start_service(self):
        """Start the AI integration service"""
        try:
            self.is_running = True
            
            # Start real-time analytics engine
            realtime_task = asyncio.create_task(self.realtime_engine.start_monitoring())
            
            # Start analysis processor
            processor_task = asyncio.create_task(self._process_analysis_queue())
            
            logger.info("🤖 AI Integration Service started successfully")
            
            # Keep service running
            await asyncio.gather(realtime_task, processor_task)
            
        except Exception as e:
            logger.error(f"Error starting AI service: {e}")
            self.is_running = False
    
    async def stop_service(self):
        """Stop the AI integration service"""
        self.is_running = False
        self.realtime_engine.stop_monitoring()
        self.executor.shutdown(wait=True)
        logger.info("AI Integration Service stopped")
    
    async def analyze_scraped_data(self, 
                                 data: List[Dict[str, Any]], 
                                 analysis_type: str = 'full',
                                 options: Dict[str, Any] = None) -> AnalysisResult:
        """Analyze scraped data with AI insights and visualizations"""
        start_time = datetime.now()
        request_id = f"analysis_{int(start_time.timestamp() * 1000)}"
        
        try:
            logger.info(f"🔍 Starting analysis {request_id} for {len(data)} data points")
            
            # Create analysis request
            request = AnalysisRequest(
                request_id=request_id,
                data=data,
                analysis_type=analysis_type,
                options=options or {},
                timestamp=start_time
            )
            
            # Add to real-time monitoring
            for item in data:
                self.realtime_engine.add_data_point(item)
            
            # Perform analysis based on type
            if analysis_type == 'full':
                insights = await self._perform_full_analysis(data)
            elif analysis_type == 'clustering':
                insights = await self._perform_clustering_analysis(data)
            elif analysis_type == 'trends':
                insights = await self._perform_trend_analysis(data)
            elif analysis_type == 'realtime':
                insights = self._get_realtime_insights()
            else:
                insights = await self._perform_full_analysis(data)
            
            # Generate visualizations
            visualizations = await self._generate_visualizations(insights)
            
            # Extract recommendations
            recommendations = insights.get('recommendations', [])
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Create result
            result = AnalysisResult(
                request_id=request_id,
                insights=insights,
                visualizations=visualizations,
                recommendations=recommendations,
                processing_time=processing_time,
                timestamp=datetime.now()
            )
            
            # Cache result
            self.results_cache[request_id] = result
            
            # Update performance metrics
            self.analysis_count += 1
            self.total_processing_time += processing_time
            
            logger.info(f"✅ Analysis {request_id} completed in {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in analysis {request_id}: {e}")
            
            # Return error result
            return AnalysisResult(
                request_id=request_id,
                insights={"error": str(e)},
                visualizations={},
                recommendations=["Review data quality and try again"],
                processing_time=(datetime.now() - start_time).total_seconds(),
                timestamp=datetime.now()
            )
    
    async def _perform_full_analysis(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform comprehensive analysis"""
        logger.info("Performing full AI analysis...")
        
        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        insights = await loop.run_in_executor(
            self.executor,
            lambda: asyncio.run(self.insights_generator.generate_comprehensive_insights(data))
        )
        
        return insights
    
    async def _perform_clustering_analysis(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform clustering-focused analysis"""
        logger.info("Performing clustering analysis...")
        
        loop = asyncio.get_event_loop()
        
        def run_clustering():
            df = self.data_processor.process_scraped_data(data)
            clustering_results = self.insights_generator.clustering.analyze_content_clusters(df)
            return {"clustering": clustering_results}
        
        return await loop.run_in_executor(self.executor, run_clustering)
    
    async def _perform_trend_analysis(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform trend-focused analysis"""
        logger.info("Performing trend analysis...")
        
        loop = asyncio.get_event_loop()
        
        def run_trends():
            df = self.data_processor.process_scraped_data(data)
            trend_results = self.insights_generator.analytics.analyze_trends(df)
            return {"trends": trend_results}
        
        return await loop.run_in_executor(self.executor, run_trends)
    
    def _get_realtime_insights(self) -> Dict[str, Any]:
        """Get real-time insights from monitoring engine"""
        logger.info("Getting real-time insights...")
        return self.realtime_engine.get_dashboard_data()
    
    async def _generate_visualizations(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """Generate visualizations for insights"""
        logger.info("Generating AI-powered visualizations...")
        
        loop = asyncio.get_event_loop()
        visualizations = await loop.run_in_executor(
            self.executor,
            self.visualizer.create_comprehensive_visualization_suite,
            insights
        )
        
        return visualizations
    
    async def _process_analysis_queue(self):
        """Process queued analysis requests"""
        while self.is_running:
            try:
                # Wait for analysis request
                request = await asyncio.wait_for(self.analysis_queue.get(), timeout=1.0)
                
                # Process the request
                result = await self.analyze_scraped_data(
                    request.data,
                    request.analysis_type,
                    request.options
                )
                
                logger.info(f"Processed queued analysis: {result.request_id}")
                
            except asyncio.TimeoutError:
                # No requests in queue, continue
                continue
            except Exception as e:
                logger.error(f"Error processing analysis queue: {e}")
    
    async def queue_analysis(self, 
                           data: List[Dict[str, Any]], 
                           analysis_type: str = 'full',
                           options: Dict[str, Any] = None) -> str:
        """Queue analysis request for background processing"""
        request_id = f"queued_{int(datetime.now().timestamp() * 1000)}"
        
        request = AnalysisRequest(
            request_id=request_id,
            data=data,
            analysis_type=analysis_type,
            options=options or {},
            timestamp=datetime.now()
        )
        
        await self.analysis_queue.put(request)
        logger.info(f"Queued analysis request: {request_id}")
        
        return request_id
    
    def get_analysis_result(self, request_id: str) -> Optional[AnalysisResult]:
        """Get analysis result by request ID"""
        return self.results_cache.get(request_id)
    
    def get_realtime_dashboard_data(self) -> Dict[str, Any]:
        """Get real-time dashboard data"""
        return self.realtime_engine.get_dashboard_data()
    
    def get_service_statistics(self) -> Dict[str, Any]:
        """Get service performance statistics"""
        avg_processing_time = (
            self.total_processing_time / self.analysis_count 
            if self.analysis_count > 0 else 0
        )
        
        return {
            "service_status": "running" if self.is_running else "stopped",
            "total_analyses": self.analysis_count,
            "average_processing_time": avg_processing_time,
            "cache_size": len(self.results_cache),
            "queue_size": self.analysis_queue.qsize() if hasattr(self.analysis_queue, 'qsize') else 0,
            "realtime_data_points": len(self.realtime_engine.analyzer.data_buffer),
            "uptime": datetime.now().isoformat()
        }
    
    async def generate_ai_recommendations(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate AI-powered recommendations for data improvement"""
        try:
            # Quick analysis for recommendations
            analysis = await self._perform_full_analysis(data)
            
            recommendations = []
            
            # Content quality recommendations
            if analysis.get('data_statistics', {}).get('avg_quality_score', 0) < 0.5:
                recommendations.append({
                    "type": "quality_improvement",
                    "priority": "high",
                    "title": "Improve Content Quality",
                    "description": "Consider adding more detailed content, images, and better structure",
                    "impact": "high"
                })
            
            # Clustering insights
            if analysis.get('clustering', {}).get('silhouette_score', 0) < 0.3:
                recommendations.append({
                    "type": "content_diversity",
                    "priority": "medium", 
                    "title": "Increase Content Diversity",
                    "description": "Add more varied content types to improve clustering",
                    "impact": "medium"
                })
            
            # Volume recommendations
            if len(data) < 50:
                recommendations.append({
                    "type": "data_volume",
                    "priority": "medium",
                    "title": "Increase Data Volume",
                    "description": "Collect more data points for better AI insights",
                    "impact": "high"
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating AI recommendations: {e}")
            return []
    
    async def optimize_scraping_strategy(self, current_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """AI-powered scraping strategy optimization"""
        try:
            analysis = await self._perform_full_analysis(current_data)
            
            optimization_strategy = {
                "recommended_targets": [],
                "quality_improvements": [],
                "efficiency_optimizations": [],
                "content_gaps": []
            }
            
            # Analyze current performance
            avg_quality = analysis.get('data_statistics', {}).get('avg_quality_score', 0)
            
            if avg_quality < 0.6:
                optimization_strategy["quality_improvements"].append({
                    "strategy": "target_higher_quality_sources",
                    "description": "Focus on sources with better content structure and media",
                    "expected_improvement": "20-30% quality increase"
                })
            
            # Clustering analysis for gaps
            clusters = analysis.get('clustering', {}).get('clusters', {})
            if len(clusters) < 3:
                optimization_strategy["content_gaps"].append({
                    "gap": "content_diversity",
                    "recommendation": "Expand to different content categories",
                    "target_clusters": "5-7 distinct content clusters"
                })
            
            return optimization_strategy
            
        except Exception as e:
            logger.error(f"Error optimizing scraping strategy: {e}")
            return {}

# Create global instance
ai_service = AIIntegrationService()

# Export main components
__all__ = [
    'AIIntegrationService',
    'AnalysisRequest',
    'AnalysisResult',
    'ai_service'
]
