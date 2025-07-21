"""
Analysis Orchestrator

Coordinates all analysis components:
- Entity Resolution
- Relationship Mapping
- Data Enrichment
- Event Detection
- Result aggregation and reporting
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any, Union
import json
from pathlib import Path

from .entity_resolver import AdvancedEntityResolver
from .relationship_mapper import EntityRelationshipMapper
from .enrichment_engine import DataEnrichmentEngine
from .event_detector import BusinessEventDetector, EventSeverity

logger = logging.getLogger(__name__)


@dataclass
class AnalysisRequest:
    """Request configuration for analysis pipeline"""
    request_id: str
    entities: List[Dict[str, Any]]
    analysis_types: List[str] = field(default_factory=lambda: ['entity_resolution', 'relationship_mapping', 'enrichment', 'event_detection'])
    enrichment_sources: List[str] = field(default_factory=lambda: ['sanctions', 'contracts', 'financial'])
    relationship_types: List[str] = field(default_factory=lambda: ['officer', 'ownership', 'address', 'contact'])
    confidence_threshold: float = 0.7
    include_low_confidence: bool = False
    max_related_entities: int = 100
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisResult:
    """Comprehensive analysis results"""
    request_id: str
    analysis_date: datetime
    summary: Dict[str, Any]
    entity_resolutions: List[Dict[str, Any]] = field(default_factory=list)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    enrichments: List[Dict[str, Any]] = field(default_factory=list)
    events: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class AnalysisOrchestrator:
    """Central coordinator for all analysis operations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Initialize analysis components
        self.entity_resolver = AdvancedEntityResolver(config.get('entity_resolution', {}))
        self.relationship_mapper = EntityRelationshipMapper(config.get('relationship_mapping', {}))
        self.enrichment_engine = DataEnrichmentEngine(config.get('enrichment', {}))
        self.event_detector = BusinessEventDetector(config.get('event_detection', {}))
        
        # Analysis state
        self.active_requests = {}
        self.completed_requests = {}
        
        # Performance metrics
        self.orchestrator_metrics = {
            'total_requests': 0,
            'successful_analyses': 0,
            'failed_analyses': 0,
            'average_duration': 0.0,
            'total_entities_processed': 0
        }
    
    async def run_comprehensive_analysis(self, request: AnalysisRequest) -> AnalysisResult:
        """Execute comprehensive analysis pipeline"""
        start_time = datetime.utcnow()
        logger.info(f"Starting comprehensive analysis for request {request.request_id}")
        
        # Initialize result container
        result = AnalysisResult(
            request_id=request.request_id,
            analysis_date=start_time,
            summary={}
        )
        
        try:
            # Track request
            self.active_requests[request.request_id] = request
            self.orchestrator_metrics['total_requests'] += 1
            self.orchestrator_metrics['total_entities_processed'] += len(request.entities)
            
            # Execute analysis steps
            if 'entity_resolution' in request.analysis_types:
                await self._run_entity_resolution(request, result)
            
            if 'relationship_mapping' in request.analysis_types:
                await self._run_relationship_mapping(request, result)
            
            if 'enrichment' in request.analysis_types:
                await self._run_enrichment(request, result)
            
            if 'event_detection' in request.analysis_types:
                await self._run_event_detection(request, result)
            
            # Generate summary
            self._generate_analysis_summary(request, result)
            
            # Calculate metrics
            duration = (datetime.utcnow() - start_time).total_seconds()
            result.metrics = {
                'duration_seconds': duration,
                'entities_processed': len(request.entities),
                'resolutions_found': len(result.entity_resolutions),
                'relationships_found': len(result.relationships),
                'enrichments_found': len(result.enrichments),
                'events_detected': len(result.events)
            }
            
            # Update orchestrator metrics
            self.orchestrator_metrics['successful_analyses'] += 1
            self._update_average_duration(duration)
            
            logger.info(f"Analysis completed for request {request.request_id} in {duration:.2f}s")
            
        except Exception as e:
            logger.error(f"Analysis failed for request {request.request_id}: {e}")
            result.errors.append(f"Analysis pipeline failed: {str(e)}")
            self.orchestrator_metrics['failed_analyses'] += 1
        
        finally:
            # Move to completed requests
            if request.request_id in self.active_requests:
                del self.active_requests[request.request_id]
            self.completed_requests[request.request_id] = result
        
        return result
    
    async def _run_entity_resolution(self, request: AnalysisRequest, result: AnalysisResult):
        """Execute entity resolution analysis"""
        logger.info("Running entity resolution analysis")
        
        try:
            # Resolve entities
            entity_clusters = await asyncio.to_thread(
                self.entity_resolver.resolve_entities, request.entities
            )
            
            # Convert to serializable format
            for cluster_id, cluster_data in entity_clusters.items():
                resolution = {
                    'cluster_id': cluster_id,
                    'entities': cluster_data['entities'],
                    'canonical_entity': cluster_data['canonical_entity'],
                    'confidence_score': cluster_data['confidence_score'],
                    'resolution_method': cluster_data.get('resolution_method', 'unknown'),
                    'similarity_scores': cluster_data.get('similarity_scores', {})
                }
                result.entity_resolutions.append(resolution)
            
            logger.info(f"Entity resolution completed: {len(entity_clusters)} clusters found")
            
        except Exception as e:
            error_msg = f"Entity resolution failed: {str(e)}"
            logger.error(error_msg)
            result.errors.append(error_msg)
    
    async def _run_relationship_mapping(self, request: AnalysisRequest, result: AnalysisResult):
        """Execute relationship mapping analysis"""
        logger.info("Running relationship mapping analysis")
        
        try:
            # Extract relationships
            relationship_results = await asyncio.to_thread(
                self.relationship_mapper.extract_relationships,
                request.entities,
                request.relationship_types
            )
            
            # Convert relationships to serializable format
            for relationship in relationship_results:
                rel_dict = {
                    'source_entity': relationship.source_entity,
                    'target_entity': relationship.target_entity,
                    'relationship_type': relationship.relationship_type,
                    'confidence_score': relationship.confidence_score,
                    'metadata': relationship.metadata,
                    'evidence': relationship.evidence
                }
                result.relationships.append(rel_dict)
            
            # Build network graph if relationships found
            if result.relationships:
                graph_metrics = await asyncio.to_thread(
                    self.relationship_mapper.build_network_graph, 
                    relationship_results
                )
                
                result.summary['network_metrics'] = {
                    'total_nodes': graph_metrics.get('node_count', 0),
                    'total_edges': graph_metrics.get('edge_count', 0),
                    'connected_components': graph_metrics.get('components', 0),
                    'density': graph_metrics.get('density', 0.0),
                    'clustering_coefficient': graph_metrics.get('clustering', 0.0)
                }
            
            logger.info(f"Relationship mapping completed: {len(result.relationships)} relationships found")
            
        except Exception as e:
            error_msg = f"Relationship mapping failed: {str(e)}"
            logger.error(error_msg)
            result.errors.append(error_msg)
    
    async def _run_enrichment(self, request: AnalysisRequest, result: AnalysisResult):
        """Execute data enrichment analysis"""
        logger.info("Running data enrichment analysis")
        
        try:
            # Enrich entities
            enrichment_results = await self.enrichment_engine.enrich_entities(
                request.entities, request.enrichment_sources
            )
            
            # Convert to serializable format
            for enrichment in enrichment_results:
                enrich_dict = {
                    'entity_id': enrichment.entity_id,
                    'source_name': enrichment.source_name,
                    'enrichment_type': enrichment.enrichment_type,
                    'data': enrichment.data,
                    'confidence_score': enrichment.confidence_score,
                    'metadata': enrichment.metadata,
                    'cost': enrichment.cost,
                    'created_at': enrichment.created_at.isoformat()
                }
                result.enrichments.append(enrich_dict)
            
            logger.info(f"Data enrichment completed: {len(enrichment_results)} enrichments found")
            
        except Exception as e:
            error_msg = f"Data enrichment failed: {str(e)}"
            logger.error(error_msg)
            result.errors.append(error_msg)
    
    async def _run_event_detection(self, request: AnalysisRequest, result: AnalysisResult):
        """Execute event detection analysis"""
        logger.info("Running event detection analysis")
        
        try:
            # Prepare data sources for event detection
            data_sources = self._prepare_event_data_sources(request.entities)
            
            # Detect events
            detected_events = await self.event_detector.detect_events(
                data_sources, 
                [entity.get('name', '') for entity in request.entities]
            )
            
            # Convert to serializable format
            for event in detected_events:
                event_dict = {
                    'event_id': event.event_id,
                    'entity_id': event.entity_id,
                    'event_type': event.event_type,
                    'category': event.category.value,
                    'severity': event.severity.value,
                    'title': event.title,
                    'description': event.description,
                    'event_date': event.event_date.isoformat(),
                    'detection_date': event.detection_date.isoformat(),
                    'confidence_score': event.confidence_score,
                    'source': event.source,
                    'source_url': event.source_url,
                    'metadata': event.metadata,
                    'related_entities': event.related_entities
                }
                result.events.append(event_dict)
            
            logger.info(f"Event detection completed: {len(detected_events)} events detected")
            
        except Exception as e:
            error_msg = f"Event detection failed: {str(e)}"
            logger.error(error_msg)
            result.errors.append(error_msg)
    
    def _prepare_event_data_sources(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare data sources for event detection"""
        data_sources = []
        
        # Convert entity data to event detection format
        for entity in entities:
            # Create structured data source
            data_sources.append({
                'type': 'structured_data',
                'data': [entity],
                'url': None
            })
            
            # If entity has associated content, create content sources
            if 'content' in entity:
                data_sources.append({
                    'type': 'news_articles',
                    'data': [{
                        'title': entity.get('name', ''),
                        'content': entity['content'],
                        'published_date': entity.get('date'),
                        'entity_id': entity.get('entity_id', '')
                    }],
                    'url': entity.get('source_url')
                })
        
        return data_sources
    
    def _generate_analysis_summary(self, request: AnalysisRequest, result: AnalysisResult):
        """Generate comprehensive analysis summary"""
        summary = {
            'request_id': request.request_id,
            'analysis_types': request.analysis_types,
            'entities_analyzed': len(request.entities),
            'total_findings': len(result.entity_resolutions) + len(result.relationships) + 
                            len(result.enrichments) + len(result.events),
            'confidence_stats': self._calculate_confidence_stats(result),
            'risk_assessment': self._assess_risk_level(result),
            'recommendations': self._generate_recommendations(result)
        }
        
        # Add type-specific summaries
        if result.entity_resolutions:
            summary['entity_resolution_summary'] = {
                'total_clusters': len(result.entity_resolutions),
                'avg_confidence': sum(r['confidence_score'] for r in result.entity_resolutions) / len(result.entity_resolutions),
                'high_confidence_clusters': len([r for r in result.entity_resolutions if r['confidence_score'] > 0.8])
            }
        
        if result.relationships:
            summary['relationship_summary'] = {
                'total_relationships': len(result.relationships),
                'relationship_types': list(set(r['relationship_type'] for r in result.relationships)),
                'avg_confidence': sum(r['confidence_score'] for r in result.relationships) / len(result.relationships)
            }
        
        if result.enrichments:
            summary['enrichment_summary'] = {
                'total_enrichments': len(result.enrichments),
                'enrichment_types': list(set(e['enrichment_type'] for e in result.enrichments)),
                'sources_used': list(set(e['source_name'] for e in result.enrichments))
            }
        
        if result.events:
            summary['event_summary'] = {
                'total_events': len(result.events),
                'high_severity_events': len([e for e in result.events if e['severity'] in ['high', 'critical']]),
                'event_categories': list(set(e['category'] for e in result.events)),
                'recent_events': len([e for e in result.events if 
                                    datetime.fromisoformat(e['detection_date']) > datetime.utcnow() - timedelta(days=7)])
            }
        
        result.summary = summary
    
    def _calculate_confidence_stats(self, result: AnalysisResult) -> Dict[str, float]:
        """Calculate confidence statistics across all results"""
        all_scores = []
        
        # Collect all confidence scores
        all_scores.extend([r['confidence_score'] for r in result.entity_resolutions])
        all_scores.extend([r['confidence_score'] for r in result.relationships])
        all_scores.extend([e['confidence_score'] for e in result.enrichments])
        all_scores.extend([e['confidence_score'] for e in result.events])
        
        if not all_scores:
            return {'avg': 0.0, 'min': 0.0, 'max': 0.0}
        
        return {
            'avg': sum(all_scores) / len(all_scores),
            'min': min(all_scores),
            'max': max(all_scores),
            'high_confidence_count': len([s for s in all_scores if s > 0.8])
        }
    
    def _assess_risk_level(self, result: AnalysisResult) -> str:
        """Assess overall risk level based on findings"""
        risk_factors = 0
        
        # Check for sanctions matches
        sanctions_matches = [e for e in result.enrichments if e['enrichment_type'] == 'sanctions' and e['data']]
        if sanctions_matches:
            risk_factors += 10
        
        # Check for critical events
        critical_events = [e for e in result.events if e['severity'] == 'critical']
        risk_factors += len(critical_events) * 3
        
        # Check for high-severity events
        high_events = [e for e in result.events if e['severity'] == 'high']
        risk_factors += len(high_events) * 2
        
        # Check for legal/regulatory issues
        legal_events = [e for e in result.events if e['category'] in ['legal', 'regulatory']]
        risk_factors += len(legal_events)
        
        # Assess risk level
        if risk_factors >= 10:
            return 'CRITICAL'
        elif risk_factors >= 5:
            return 'HIGH'
        elif risk_factors >= 2:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _generate_recommendations(self, result: AnalysisResult) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        # Risk-based recommendations
        risk_level = self._assess_risk_level(result)
        if risk_level in ['HIGH', 'CRITICAL']:
            recommendations.append("Immediate review required due to high-risk findings")
            recommendations.append("Consider enhanced due diligence procedures")
        
        # Sanctions recommendations
        sanctions_matches = [e for e in result.enrichments if e['enrichment_type'] == 'sanctions' and e['data']]
        if sanctions_matches:
            recommendations.append("ALERT: Potential sanctions match detected - verify immediately")
        
        # Event-based recommendations
        critical_events = [e for e in result.events if e['severity'] == 'critical']
        if critical_events:
            recommendations.append("Monitor critical events closely - consider automated alerts")
        
        # Relationship recommendations
        complex_relationships = [r for r in result.relationships if r['confidence_score'] > 0.8]
        if len(complex_relationships) > 10:
            recommendations.append("Complex relationship network detected - consider network analysis")
        
        # Data quality recommendations
        low_confidence_count = len([r for r in result.entity_resolutions if r['confidence_score'] < 0.7])
        if low_confidence_count > len(result.entity_resolutions) * 0.3:
            recommendations.append("Consider improving data quality for better entity resolution")
        
        if not recommendations:
            recommendations.append("No immediate action required based on current analysis")
        
        return recommendations
    
    def _update_average_duration(self, new_duration: float):
        """Update average analysis duration"""
        if self.orchestrator_metrics['successful_analyses'] == 1:
            self.orchestrator_metrics['average_duration'] = new_duration
        else:
            # Exponential moving average
            alpha = 0.1
            current_avg = self.orchestrator_metrics['average_duration']
            self.orchestrator_metrics['average_duration'] = alpha * new_duration + (1 - alpha) * current_avg
    
    async def get_analysis_status(self, request_id: str) -> Dict[str, Any]:
        """Get status of analysis request"""
        if request_id in self.active_requests:
            return {'status': 'running', 'request': self.active_requests[request_id]}
        elif request_id in self.completed_requests:
            return {'status': 'completed', 'result': self.completed_requests[request_id]}
        else:
            return {'status': 'not_found'}
    
    def get_orchestrator_metrics(self) -> Dict[str, Any]:
        """Get orchestrator performance metrics"""
        return self.orchestrator_metrics.copy()
    
    async def export_analysis_results(self, request_id: str, format: str = 'json') -> Optional[str]:
        """Export analysis results in specified format"""
        if request_id not in self.completed_requests:
            return None
        
        result = self.completed_requests[request_id]
        
        if format == 'json':
            return json.dumps(result.__dict__, indent=2, default=str)
        elif format == 'summary':
            return self._format_summary_report(result)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _format_summary_report(self, result: AnalysisResult) -> str:
        """Format results as human-readable summary report"""
        report = []
        report.append(f"BUSINESS INTELLIGENCE ANALYSIS REPORT")
        report.append(f"{'=' * 50}")
        report.append(f"Request ID: {result.request_id}")
        report.append(f"Analysis Date: {result.analysis_date}")
        report.append(f"Risk Level: {result.summary.get('risk_assessment', 'UNKNOWN')}")
        report.append("")
        
        # Summary statistics
        report.append("SUMMARY STATISTICS")
        report.append("-" * 20)
        report.append(f"Entities Analyzed: {result.summary.get('entities_analyzed', 0)}")
        report.append(f"Total Findings: {result.summary.get('total_findings', 0)}")
        report.append(f"Analysis Duration: {result.metrics.get('duration_seconds', 0):.2f} seconds")
        report.append("")
        
        # High-level findings
        if result.events:
            critical_events = [e for e in result.events if e['severity'] == 'critical']
            high_events = [e for e in result.events if e['severity'] == 'high']
            
            if critical_events or high_events:
                report.append("HIGH PRIORITY ALERTS")
                report.append("-" * 20)
                for event in critical_events + high_events:
                    report.append(f"• {event['title']} ({event['severity'].upper()})")
                report.append("")
        
        # Recommendations
        if result.summary.get('recommendations'):
            report.append("RECOMMENDATIONS")
            report.append("-" * 15)
            for rec in result.summary['recommendations']:
                report.append(f"• {rec}")
            report.append("")
        
        return "\n".join(report)
