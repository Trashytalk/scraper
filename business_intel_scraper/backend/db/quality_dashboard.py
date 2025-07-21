"""
Data Quality Dashboard System

Provides visualization and monitoring interfaces for data quality metrics,
provenance tracking, and correction management.
"""

import logging
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, text
from sqlalchemy.orm import selectinload

from .quality_models import (
    DataSource, EntityRecord, QualityAssessment, DataCorrection,
    DataChangeLog, QualityAlert, ProvenanceRecord
)
from .quality_engine import quality_engine
from .provenance_tracker import provenance_tracker
from .correction_system import correction_manager, CorrectionStatus

logger = logging.getLogger(__name__)


class DashboardTimeRange(str, Enum):
    """Time range options for dashboard views"""
    LAST_HOUR = "1h"
    LAST_DAY = "24h"
    LAST_WEEK = "7d"
    LAST_MONTH = "30d"
    LAST_QUARTER = "90d"
    LAST_YEAR = "365d"
    ALL_TIME = "all"


class MetricType(str, Enum):
    """Types of quality metrics"""
    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"
    FRESHNESS = "freshness"
    CONFIDENCE = "confidence"
    OVERALL = "overall"
    ERROR_RATE = "error_rate"
    DUPLICATE_RATE = "duplicate_rate"


@dataclass
class QualityMetric:
    """Quality metric data point"""
    timestamp: datetime
    metric_type: MetricType
    value: float
    entity_count: int
    metadata: Dict[str, Any] = None


@dataclass
class SourceQualityReport:
    """Quality report for a data source"""
    source_id: str
    source_name: str
    url_pattern: str
    reliability_score: float
    entity_count: int
    quality_metrics: Dict[str, float]
    recent_errors: List[Dict[str, Any]]
    last_scraped: Optional[datetime]
    trend: str  # "improving", "declining", "stable"


@dataclass
class EntityQualityReport:
    """Quality report for individual entities"""
    entity_id: str
    entity_type: str
    quality_score: float
    quality_breakdown: Dict[str, float]
    issue_count: int
    top_issues: List[str]
    source_count: int
    last_updated: datetime
    correction_suggestions: int


class QualityDashboard:
    """Main dashboard for data quality monitoring"""
    
    def __init__(self):
        self.cache_ttl = timedelta(minutes=15)  # Cache dashboard data for 15 minutes
        self._metric_cache = {}
    
    async def get_overview_metrics(self, session: AsyncSession,
                                 time_range: DashboardTimeRange = DashboardTimeRange.LAST_DAY) -> Dict[str, Any]:
        """Get high-level quality overview metrics"""
        logger.info(f"Generating overview metrics for {time_range}")
        
        # Calculate time bounds
        time_filter = self._get_time_filter(time_range)
        
        # Basic entity counts
        total_entities_query = select(func.count(EntityRecord.id)).where(EntityRecord.is_active == True)
        total_entities = (await session.execute(total_entities_query)).scalar()
        
        # Quality distribution
        quality_dist_query = (
            select(
                func.count(EntityRecord.id).label('count'),
                func.avg(EntityRecord.overall_quality_score).label('avg_quality')
            )
            .where(EntityRecord.is_active == True)
        )
        
        if time_filter:
            quality_dist_query = quality_dist_query.where(EntityRecord.updated_at >= time_filter)
        
        quality_stats = (await session.execute(quality_dist_query)).first()
        
        # Issue counts
        entities_with_issues_query = (
            select(func.count(EntityRecord.id))
            .where(
                and_(
                    EntityRecord.is_active == True,
                    EntityRecord.has_issues == True
                )
            )
        )
        
        if time_filter:
            entities_with_issues_query = entities_with_issues_query.where(EntityRecord.updated_at >= time_filter)
        
        entities_with_issues = (await session.execute(entities_with_issues_query)).scalar()
        
        # Duplicate counts
        duplicate_entities_query = (
            select(func.count(EntityRecord.id))
            .where(EntityRecord.is_duplicate == True)
        )
        duplicates = (await session.execute(duplicate_entities_query)).scalar()
        
        # Recent corrections
        corrections_query = (
            select(func.count(DataCorrection.correction_id))
            .where(DataCorrection.status == CorrectionStatus.PENDING)
        )
        pending_corrections = (await session.execute(corrections_query)).scalar()
        
        # Recent alerts
        alerts_query = (
            select(func.count(QualityAlert.alert_id))
            .where(QualityAlert.is_resolved == False)
        )
        
        if time_filter:
            alerts_query = alerts_query.where(QualityAlert.triggered_at >= time_filter)
        
        active_alerts = (await session.execute(alerts_query)).scalar()
        
        # Data freshness
        freshness_query = (
            select(func.avg(
                func.extract('epoch', func.now() - EntityRecord.last_seen) / 86400
            ))
            .where(EntityRecord.is_active == True)
        )
        avg_staleness_days = (await session.execute(freshness_query)).scalar() or 0
        
        return {
            'total_entities': total_entities,
            'average_quality_score': round(quality_stats.avg_quality or 0, 2),
            'entities_with_issues': entities_with_issues,
            'issue_rate': round((entities_with_issues / max(total_entities, 1)) * 100, 1),
            'duplicate_entities': duplicates,
            'duplicate_rate': round((duplicates / max(total_entities, 1)) * 100, 1),
            'pending_corrections': pending_corrections,
            'active_alerts': active_alerts,
            'avg_staleness_days': round(avg_staleness_days, 1),
            'data_freshness_score': max(0, min(100, 100 - (avg_staleness_days * 5))),
            'time_range': time_range,
            'generated_at': datetime.now(timezone.utc).isoformat()
        }
    
    async def get_quality_trends(self, session: AsyncSession,
                               time_range: DashboardTimeRange = DashboardTimeRange.LAST_WEEK,
                               metric_type: MetricType = MetricType.OVERALL) -> List[QualityMetric]:
        """Get quality trend data over time"""
        logger.info(f"Generating quality trends for {metric_type} over {time_range}")
        
        # Calculate time bounds and intervals
        time_filter = self._get_time_filter(time_range)
        interval = self._get_time_interval(time_range)
        
        if not time_filter:
            # For "all time", limit to last year with weekly intervals
            time_filter = datetime.now(timezone.utc) - timedelta(days=365)
            interval = "7 days"
        
        # Build query for quality assessments over time
        query = text(f"""
            SELECT 
                date_trunc('{interval.split()[1]}', assessed_at) as time_bucket,
                AVG(CASE WHEN '{metric_type}' = 'overall' THEN overall_score
                         WHEN '{metric_type}' = 'completeness' THEN completeness_score
                         WHEN '{metric_type}' = 'consistency' THEN consistency_score
                         WHEN '{metric_type}' = 'freshness' THEN freshness_score
                         WHEN '{metric_type}' = 'confidence' THEN confidence_score
                         ELSE overall_score END) as avg_score,
                COUNT(*) as entity_count
            FROM quality_assessments qa
            JOIN entity_records er ON qa.entity_id = er.id
            WHERE qa.assessed_at >= :time_filter
                AND er.is_active = true
            GROUP BY time_bucket
            ORDER BY time_bucket
        """)
        
        result = await session.execute(query, {'time_filter': time_filter})
        
        trends = []
        for row in result:
            trends.append(QualityMetric(
                timestamp=row.time_bucket,
                metric_type=metric_type,
                value=round(float(row.avg_score), 3),
                entity_count=int(row.entity_count)
            ))
        
        return trends
    
    async def get_source_quality_reports(self, session: AsyncSession,
                                       limit: int = 20) -> List[SourceQualityReport]:
        """Get quality reports for data sources"""
        logger.info(f"Generating source quality reports (limit: {limit})")
        
        # Get sources with their quality metrics
        sources_query = (
            select(DataSource)
            .where(DataSource.is_active == True)
            .order_by(desc(DataSource.reliability_score))
            .limit(limit)
        )
        
        sources = (await session.execute(sources_query)).scalars().all()
        
        reports = []
        for source in sources:
            # Get quality metrics for entities from this source
            metrics_query = text("""
                SELECT 
                    AVG(er.overall_quality_score) as avg_overall,
                    AVG(qa.completeness_score) as avg_completeness,
                    AVG(qa.consistency_score) as avg_consistency,
                    AVG(qa.freshness_score) as avg_freshness,
                    AVG(qa.confidence_score) as avg_confidence,
                    COUNT(DISTINCT er.id) as entity_count
                FROM entity_records er
                JOIN provenance_records pr ON er.id = pr.entity_id
                LEFT JOIN quality_assessments qa ON er.id = qa.entity_id
                WHERE pr.source_url LIKE :url_pattern
                    AND er.is_active = true
            """)
            
            metrics_result = await session.execute(
                metrics_query, 
                {'url_pattern': f"{source.url_pattern}%"}
            )
            metrics_row = metrics_result.first()
            
            # Get recent errors from this source
            errors_query = text("""
                SELECT 
                    pr.extraction_error,
                    pr.created_at,
                    COUNT(*) as error_count
                FROM provenance_records pr
                WHERE pr.source_url LIKE :url_pattern
                    AND pr.extraction_error IS NOT NULL
                    AND pr.created_at >= :since
                GROUP BY pr.extraction_error, pr.created_at
                ORDER BY pr.created_at DESC
                LIMIT 5
            """)
            
            errors_result = await session.execute(errors_query, {
                'url_pattern': f"{source.url_pattern}%",
                'since': datetime.now(timezone.utc) - timedelta(days=7)
            })
            
            recent_errors = []
            for error_row in errors_result:
                recent_errors.append({
                    'error': error_row.extraction_error,
                    'timestamp': error_row.created_at.isoformat(),
                    'count': error_row.error_count
                })
            
            # Calculate trend
            trend = await self._calculate_source_trend(source, session)
            
            quality_metrics = {
                'overall': round(metrics_row.avg_overall or 0, 3),
                'completeness': round(metrics_row.avg_completeness or 0, 3),
                'consistency': round(metrics_row.avg_consistency or 0, 3),
                'freshness': round(metrics_row.avg_freshness or 0, 3),
                'confidence': round(metrics_row.avg_confidence or 0, 3)
            }
            
            reports.append(SourceQualityReport(
                source_id=source.source_id,
                source_name=source.name,
                url_pattern=source.url_pattern,
                reliability_score=source.reliability_score,
                entity_count=metrics_row.entity_count or 0,
                quality_metrics=quality_metrics,
                recent_errors=recent_errors,
                last_scraped=source.last_scraped,
                trend=trend
            ))
        
        return reports
    
    async def get_entity_quality_reports(self, session: AsyncSession,
                                       entity_type: Optional[str] = None,
                                       quality_threshold: float = 0.5,
                                       limit: int = 50) -> List[EntityQualityReport]:
        """Get quality reports for individual entities"""
        logger.info(f"Generating entity quality reports (type: {entity_type}, limit: {limit})")
        
        # Build query for low-quality entities
        query = (
            select(EntityRecord)
            .where(
                and_(
                    EntityRecord.is_active == True,
                    EntityRecord.overall_quality_score < quality_threshold
                )
            )
            .options(selectinload(EntityRecord.quality_assessments))
            .order_by(EntityRecord.overall_quality_score.asc())
            .limit(limit)
        )
        
        if entity_type:
            query = query.where(EntityRecord.entity_type == entity_type)
        
        entities = (await session.execute(query)).scalars().all()
        
        reports = []
        for entity in entities:
            # Get latest quality assessment
            latest_assessment = None
            if entity.quality_assessments:
                latest_assessment = max(entity.quality_assessments, key=lambda x: x.assessed_at)
            
            quality_breakdown = {}
            if latest_assessment:
                quality_breakdown = {
                    'completeness': latest_assessment.completeness_score,
                    'consistency': latest_assessment.consistency_score,
                    'freshness': latest_assessment.freshness_score,
                    'confidence': latest_assessment.confidence_score
                }
            
            # Get top issues
            issues = []
            if latest_assessment and latest_assessment.issues:
                issues = latest_assessment.issues.get('issues', [])[:3]  # Top 3 issues
            
            # Count sources
            sources_query = (
                select(func.count(func.distinct(ProvenanceRecord.source_url)))
                .where(ProvenanceRecord.entity_id == entity.id)
            )
            source_count = (await session.execute(sources_query)).scalar()
            
            # Count correction suggestions
            corrections_query = (
                select(func.count(DataCorrection.correction_id))
                .where(
                    and_(
                        DataCorrection.entity_id == entity.id,
                        DataCorrection.status == CorrectionStatus.PENDING
                    )
                )
            )
            correction_suggestions = (await session.execute(corrections_query)).scalar()
            
            reports.append(EntityQualityReport(
                entity_id=entity.entity_id,
                entity_type=entity.entity_type,
                quality_score=entity.overall_quality_score,
                quality_breakdown=quality_breakdown,
                issue_count=len(issues) if issues else 0,
                top_issues=issues,
                source_count=source_count or 0,
                last_updated=entity.updated_at,
                correction_suggestions=correction_suggestions or 0
            ))
        
        return reports
    
    async def get_alerts_summary(self, session: AsyncSession,
                               time_range: DashboardTimeRange = DashboardTimeRange.LAST_DAY) -> Dict[str, Any]:
        """Get summary of quality alerts"""
        logger.info(f"Generating alerts summary for {time_range}")
        
        time_filter = self._get_time_filter(time_range)
        
        # Base query for alerts
        base_query = select(QualityAlert)
        if time_filter:
            base_query = base_query.where(QualityAlert.triggered_at >= time_filter)
        
        # Total alerts
        total_alerts = await session.execute(
            select(func.count()).select_from(base_query.subquery())
        )
        total_count = total_alerts.scalar()
        
        # Active (unresolved) alerts
        active_alerts = await session.execute(
            base_query.where(QualityAlert.is_resolved == False)
        )
        active_count = len(active_alerts.scalars().all())
        
        # Alerts by severity
        severity_query = (
            select(
                QualityAlert.severity,
                func.count(QualityAlert.alert_id).label('count')
            )
            .group_by(QualityAlert.severity)
        )
        
        if time_filter:
            severity_query = severity_query.where(QualityAlert.triggered_at >= time_filter)
        
        severity_result = await session.execute(severity_query)
        severity_breakdown = {row.severity: row.count for row in severity_result}
        
        # Alerts by type
        type_query = (
            select(
                QualityAlert.alert_type,
                func.count(QualityAlert.alert_id).label('count')
            )
            .group_by(QualityAlert.alert_type)
        )
        
        if time_filter:
            type_query = type_query.where(QualityAlert.triggered_at >= time_filter)
        
        type_result = await session.execute(type_query)
        type_breakdown = {row.alert_type: row.count for row in type_result}
        
        # Recent critical alerts
        critical_alerts_query = (
            base_query
            .where(
                and_(
                    QualityAlert.severity == 'critical',
                    QualityAlert.is_resolved == False
                )
            )
            .order_by(desc(QualityAlert.triggered_at))
            .limit(10)
        )
        
        critical_alerts = (await session.execute(critical_alerts_query)).scalars().all()
        
        critical_alerts_data = []
        for alert in critical_alerts:
            critical_alerts_data.append({
                'alert_id': alert.alert_id,
                'alert_type': alert.alert_type,
                'entity_id': alert.entity_id,
                'message': alert.message,
                'triggered_at': alert.triggered_at.isoformat(),
                'metadata': alert.metadata
            })
        
        return {
            'total_alerts': total_count,
            'active_alerts': active_count,
            'resolution_rate': round(((total_count - active_count) / max(total_count, 1)) * 100, 1),
            'severity_breakdown': severity_breakdown,
            'type_breakdown': type_breakdown,
            'critical_alerts': critical_alerts_data,
            'time_range': time_range,
            'generated_at': datetime.now(timezone.utc).isoformat()
        }
    
    async def get_correction_statistics(self, session: AsyncSession,
                                      time_range: DashboardTimeRange = DashboardTimeRange.LAST_WEEK) -> Dict[str, Any]:
        """Get data correction statistics"""
        logger.info(f"Generating correction statistics for {time_range}")
        
        time_filter = self._get_time_filter(time_range)
        
        # Base query
        base_query = select(DataCorrection)
        if time_filter:
            base_query = base_query.where(DataCorrection.submitted_at >= time_filter)
        
        # Total corrections
        total_corrections = await session.execute(
            select(func.count()).select_from(base_query.subquery())
        )
        total_count = total_corrections.scalar()
        
        # Status breakdown
        status_query = (
            select(
                DataCorrection.status,
                func.count(DataCorrection.correction_id).label('count')
            )
            .group_by(DataCorrection.status)
        )
        
        if time_filter:
            status_query = status_query.where(DataCorrection.submitted_at >= time_filter)
        
        status_result = await session.execute(status_query)
        status_breakdown = {row.status: row.count for row in status_result}
        
        # Correction type breakdown
        type_query = (
            select(
                DataCorrection.correction_type,
                func.count(DataCorrection.correction_id).label('count')
            )
            .group_by(DataCorrection.correction_type)
        )
        
        if time_filter:
            type_query = type_query.where(DataCorrection.submitted_at >= time_filter)
        
        type_result = await session.execute(type_query)
        type_breakdown = {row.correction_type: row.count for row in type_result}
        
        # Auto-correction stats
        auto_corrections = await session.execute(
            base_query.where(DataCorrection.submitted_by == 'auto_correction_system')
        )
        auto_count = len(auto_corrections.scalars().all())
        
        # Average confidence
        confidence_query = (
            select(func.avg(DataCorrection.confidence))
        )
        
        if time_filter:
            confidence_query = confidence_query.where(DataCorrection.submitted_at >= time_filter)
        
        avg_confidence = (await session.execute(confidence_query)).scalar() or 0
        
        # Top contributors
        contributors_query = (
            select(
                DataCorrection.submitted_by,
                func.count(DataCorrection.correction_id).label('count')
            )
            .where(DataCorrection.submitted_by != 'auto_correction_system')
            .group_by(DataCorrection.submitted_by)
            .order_by(desc(func.count(DataCorrection.correction_id)))
            .limit(10)
        )
        
        if time_filter:
            contributors_query = contributors_query.where(DataCorrection.submitted_at >= time_filter)
        
        contributors_result = await session.execute(contributors_query)
        top_contributors = [
            {'user': row.submitted_by, 'corrections': row.count}
            for row in contributors_result
        ]
        
        return {
            'total_corrections': total_count,
            'auto_corrections': auto_count,
            'manual_corrections': total_count - auto_count,
            'automation_rate': round((auto_count / max(total_count, 1)) * 100, 1),
            'status_breakdown': status_breakdown,
            'type_breakdown': type_breakdown,
            'average_confidence': round(avg_confidence, 3),
            'top_contributors': top_contributors,
            'time_range': time_range,
            'generated_at': datetime.now(timezone.utc).isoformat()
        }
    
    def _get_time_filter(self, time_range: DashboardTimeRange) -> Optional[datetime]:
        """Convert time range to datetime filter"""
        if time_range == DashboardTimeRange.ALL_TIME:
            return None
        
        now = datetime.now(timezone.utc)
        
        time_deltas = {
            DashboardTimeRange.LAST_HOUR: timedelta(hours=1),
            DashboardTimeRange.LAST_DAY: timedelta(days=1),
            DashboardTimeRange.LAST_WEEK: timedelta(days=7),
            DashboardTimeRange.LAST_MONTH: timedelta(days=30),
            DashboardTimeRange.LAST_QUARTER: timedelta(days=90),
            DashboardTimeRange.LAST_YEAR: timedelta(days=365)
        }
        
        delta = time_deltas.get(time_range)
        return now - delta if delta else None
    
    def _get_time_interval(self, time_range: DashboardTimeRange) -> str:
        """Get appropriate time interval for aggregation"""
        intervals = {
            DashboardTimeRange.LAST_HOUR: "5 minutes",
            DashboardTimeRange.LAST_DAY: "1 hour",
            DashboardTimeRange.LAST_WEEK: "6 hours",
            DashboardTimeRange.LAST_MONTH: "1 day",
            DashboardTimeRange.LAST_QUARTER: "3 days",
            DashboardTimeRange.LAST_YEAR: "1 week",
            DashboardTimeRange.ALL_TIME: "1 month"
        }
        
        return intervals.get(time_range, "1 day")
    
    async def _calculate_source_trend(self, source: DataSource, session: AsyncSession) -> str:
        """Calculate quality trend for a data source"""
        # Get quality scores from last 30 days
        trend_query = text("""
            SELECT 
                DATE(qa.assessed_at) as assessment_date,
                AVG(qa.overall_score) as daily_avg
            FROM quality_assessments qa
            JOIN entity_records er ON qa.entity_id = er.id
            JOIN provenance_records pr ON er.id = pr.entity_id
            WHERE pr.source_url LIKE :url_pattern
                AND qa.assessed_at >= :since
                AND er.is_active = true
            GROUP BY DATE(qa.assessed_at)
            ORDER BY assessment_date
        """)
        
        since = datetime.now(timezone.utc) - timedelta(days=30)
        result = await session.execute(trend_query, {
            'url_pattern': f"{source.url_pattern}%",
            'since': since
        })
        
        daily_scores = [row.daily_avg for row in result]
        
        if len(daily_scores) < 3:
            return "stable"  # Not enough data
        
        # Simple trend calculation
        first_half = daily_scores[:len(daily_scores)//2]
        second_half = daily_scores[len(daily_scores)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        change_threshold = 0.05  # 5% change threshold
        
        if second_avg > first_avg + change_threshold:
            return "improving"
        elif second_avg < first_avg - change_threshold:
            return "declining"
        else:
            return "stable"


class DashboardAPI:
    """API interface for dashboard data"""
    
    def __init__(self):
        self.dashboard = QualityDashboard()
    
    async def get_dashboard_data(self, session: AsyncSession,
                               dashboard_type: str = "overview",
                               **kwargs) -> Dict[str, Any]:
        """Get dashboard data based on type"""
        try:
            if dashboard_type == "overview":
                return await self.dashboard.get_overview_metrics(session, **kwargs)
            
            elif dashboard_type == "trends":
                return {
                    'trends': [
                        asdict(trend) for trend in 
                        await self.dashboard.get_quality_trends(session, **kwargs)
                    ]
                }
            
            elif dashboard_type == "sources":
                return {
                    'sources': [
                        asdict(report) for report in 
                        await self.dashboard.get_source_quality_reports(session, **kwargs)
                    ]
                }
            
            elif dashboard_type == "entities":
                return {
                    'entities': [
                        asdict(report) for report in 
                        await self.dashboard.get_entity_quality_reports(session, **kwargs)
                    ]
                }
            
            elif dashboard_type == "alerts":
                return await self.dashboard.get_alerts_summary(session, **kwargs)
            
            elif dashboard_type == "corrections":
                return await self.dashboard.get_correction_statistics(session, **kwargs)
            
            else:
                raise ValueError(f"Unknown dashboard type: {dashboard_type}")
        
        except Exception as e:
            logger.error(f"Error generating dashboard data: {e}")
            raise
    
    async def export_quality_report(self, session: AsyncSession,
                                  report_type: str = "comprehensive",
                                  format: str = "json") -> Dict[str, Any]:
        """Export comprehensive quality report"""
        logger.info(f"Exporting {report_type} quality report in {format} format")
        
        report = {
            'report_type': report_type,
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'format': format
        }
        
        if report_type in ["comprehensive", "overview"]:
            report['overview'] = await self.dashboard.get_overview_metrics(session)
        
        if report_type in ["comprehensive", "sources"]:
            report['sources'] = [
                asdict(source) for source in 
                await self.dashboard.get_source_quality_reports(session, limit=100)
            ]
        
        if report_type in ["comprehensive", "entities"]:
            report['problem_entities'] = [
                asdict(entity) for entity in 
                await self.dashboard.get_entity_quality_reports(session, limit=100)
            ]
        
        if report_type in ["comprehensive", "alerts"]:
            report['alerts'] = await self.dashboard.get_alerts_summary(session)
        
        if report_type in ["comprehensive", "corrections"]:
            report['corrections'] = await self.dashboard.get_correction_statistics(session)
        
        # Add metadata
        report['metadata'] = {
            'export_timestamp': datetime.now(timezone.utc).isoformat(),
            'data_version': '1.0',
            'report_scope': report_type
        }
        
        return report


# Global dashboard instance
quality_dashboard = QualityDashboard()
dashboard_api = DashboardAPI()
