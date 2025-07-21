"""
Quality Alert System

Automated monitoring and alerting for data quality issues,
anomalies, and threshold violations.
"""

import logging
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, asdict
from enum import Enum
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, text
from sqlalchemy.orm import selectinload

from .quality_models import (
    QualityAlert, QualityRule, EntityRecord, QualityAssessment,
    DataSource, ProvenanceRecord, AlertSeverity, AlertType
)

logger = logging.getLogger(__name__)


class AlertCondition(str, Enum):
    """Alert condition types"""
    THRESHOLD_BELOW = "threshold_below"
    THRESHOLD_ABOVE = "threshold_above"
    PERCENTAGE_CHANGE = "percentage_change"
    ANOMALY_DETECTED = "anomaly_detected"
    PATTERN_BROKEN = "pattern_broken"
    STALENESS_EXCEEDED = "staleness_exceeded"


@dataclass
class AlertRule:
    """Configuration for an alert rule"""
    rule_name: str
    condition: AlertCondition
    metric_name: str
    threshold_value: float
    severity: AlertSeverity
    alert_type: AlertType
    cooldown_minutes: int = 60
    entity_type_filter: Optional[str] = None
    source_filter: Optional[str] = None
    description: str = ""
    notification_channels: List[str] = None


@dataclass
class AlertTrigger:
    """Data that triggered an alert"""
    rule_name: str
    entity_id: Optional[str]
    metric_value: float
    threshold_value: float
    severity: AlertSeverity
    alert_type: AlertType
    message: str
    metadata: Dict[str, Any]


class AlertEvaluator:
    """Evaluates conditions and triggers alerts"""
    
    def __init__(self):
        self.default_rules = self._create_default_rules()
    
    def _create_default_rules(self) -> List[AlertRule]:
        """Create default alert rules"""
        return [
            # Quality score alerts
            AlertRule(
                rule_name="critical_quality_drop",
                condition=AlertCondition.THRESHOLD_BELOW,
                metric_name="overall_quality_score",
                threshold_value=0.3,
                severity=AlertSeverity.CRITICAL,
                alert_type=AlertType.QUALITY_DROP,
                description="Entity quality score dropped below 30%",
                notification_channels=["email", "webhook"]
            ),
            
            AlertRule(
                rule_name="low_quality_warning",
                condition=AlertCondition.THRESHOLD_BELOW,
                metric_name="overall_quality_score",
                threshold_value=0.6,
                severity=AlertSeverity.WARNING,
                alert_type=AlertType.QUALITY_DROP,
                description="Entity quality score below 60%",
                cooldown_minutes=120
            ),
            
            # Completeness alerts
            AlertRule(
                rule_name="low_completeness",
                condition=AlertCondition.THRESHOLD_BELOW,
                metric_name="completeness_score",
                threshold_value=0.5,
                severity=AlertSeverity.WARNING,
                alert_type=AlertType.INCOMPLETE_DATA,
                description="Data completeness below 50%"
            ),
            
            # Staleness alerts
            AlertRule(
                rule_name="data_staleness_critical",
                condition=AlertCondition.STALENESS_EXCEEDED,
                metric_name="days_since_update",
                threshold_value=30.0,
                severity=AlertSeverity.CRITICAL,
                alert_type=AlertType.STALE_DATA,
                description="Data not updated for over 30 days"
            ),
            
            AlertRule(
                rule_name="data_staleness_warning",
                condition=AlertCondition.STALENESS_EXCEEDED,
                metric_name="days_since_update",
                threshold_value=14.0,
                severity=AlertSeverity.WARNING,
                alert_type=AlertType.STALE_DATA,
                description="Data not updated for over 14 days"
            ),
            
            # Anomaly detection
            AlertRule(
                rule_name="quality_score_anomaly",
                condition=AlertCondition.PERCENTAGE_CHANGE,
                metric_name="overall_quality_score",
                threshold_value=-20.0,  # 20% drop
                severity=AlertSeverity.HIGH,
                alert_type=AlertType.ANOMALY,
                description="Quality score dropped by more than 20%"
            ),
            
            # Error rate alerts
            AlertRule(
                rule_name="high_error_rate",
                condition=AlertCondition.THRESHOLD_ABOVE,
                metric_name="error_rate",
                threshold_value=0.1,  # 10% error rate
                severity=AlertSeverity.HIGH,
                alert_type=AlertType.EXTRACTION_ERROR,
                description="Error rate above 10%"
            ),
            
            # Duplicate detection
            AlertRule(
                rule_name="high_duplicate_rate",
                condition=AlertCondition.THRESHOLD_ABOVE,
                metric_name="duplicate_rate",
                threshold_value=0.15,  # 15% duplicate rate
                severity=AlertSeverity.MEDIUM,
                alert_type=AlertType.DUPLICATE_DATA,
                description="Duplicate rate above 15%"
            ),
            
            # Source-specific alerts
            AlertRule(
                rule_name="source_reliability_drop",
                condition=AlertCondition.THRESHOLD_BELOW,
                metric_name="source_reliability",
                threshold_value=0.7,
                severity=AlertSeverity.HIGH,
                alert_type=AlertType.SOURCE_ISSUE,
                description="Data source reliability below 70%"
            )
        ]
    
    async def evaluate_entity_alerts(self, entity: EntityRecord, 
                                   session: AsyncSession) -> List[AlertTrigger]:
        """Evaluate alert rules for a specific entity"""
        triggers = []
        
        # Get latest quality assessment
        assessment_query = (
            select(QualityAssessment)
            .where(QualityAssessment.entity_id == entity.id)
            .order_by(desc(QualityAssessment.assessed_at))
            .limit(1)
        )
        latest_assessment = (await session.execute(assessment_query)).scalar_one_or_none()
        
        if not latest_assessment:
            return triggers
        
        # Calculate staleness
        days_since_update = (datetime.now(timezone.utc) - entity.updated_at).days
        
        # Prepare metrics
        metrics = {
            'overall_quality_score': entity.overall_quality_score,
            'completeness_score': latest_assessment.completeness_score,
            'consistency_score': latest_assessment.consistency_score,
            'freshness_score': latest_assessment.freshness_score,
            'confidence_score': latest_assessment.confidence_score,
            'days_since_update': float(days_since_update)
        }
        
        # Evaluate each rule
        for rule in self.default_rules:
            # Apply entity type filter
            if rule.entity_type_filter and entity.entity_type != rule.entity_type_filter:
                continue
            
            trigger = await self._evaluate_rule(rule, entity, metrics, session)
            if trigger:
                triggers.append(trigger)
        
        return triggers
    
    async def evaluate_source_alerts(self, source: DataSource,
                                   session: AsyncSession) -> List[AlertTrigger]:
        """Evaluate alert rules for a data source"""
        triggers = []
        
        # Calculate source metrics
        metrics_query = text("""
            SELECT 
                COUNT(DISTINCT er.id) as entity_count,
                AVG(er.overall_quality_score) as avg_quality,
                COUNT(CASE WHEN pr.extraction_error IS NOT NULL THEN 1 END)::float / 
                    COUNT(*)::float as error_rate,
                COUNT(CASE WHEN er.is_duplicate THEN 1 END)::float / 
                    COUNT(*)::float as duplicate_rate
            FROM entity_records er
            JOIN provenance_records pr ON er.id = pr.entity_id
            WHERE pr.source_url LIKE :url_pattern
                AND er.is_active = true
                AND pr.created_at >= :since
        """)
        
        since = datetime.now(timezone.utc) - timedelta(days=7)
        result = await session.execute(metrics_query, {
            'url_pattern': f"{source.url_pattern}%",
            'since': since
        })
        
        metrics_row = result.first()
        if not metrics_row or metrics_row.entity_count == 0:
            return triggers
        
        metrics = {
            'source_reliability': source.reliability_score,
            'error_rate': metrics_row.error_rate or 0,
            'duplicate_rate': metrics_row.duplicate_rate or 0,
            'overall_quality_score': metrics_row.avg_quality or 0
        }
        
        # Evaluate source-specific rules
        for rule in self.default_rules:
            if rule.source_filter and not source.url_pattern.startswith(rule.source_filter):
                continue
            
            trigger = await self._evaluate_source_rule(rule, source, metrics, session)
            if trigger:
                triggers.append(trigger)
        
        return triggers
    
    async def _evaluate_rule(self, rule: AlertRule, entity: EntityRecord,
                           metrics: Dict[str, float], session: AsyncSession) -> Optional[AlertTrigger]:
        """Evaluate a single rule for an entity"""
        metric_value = metrics.get(rule.metric_name)
        if metric_value is None:
            return None
        
        triggered = False
        message = ""
        
        if rule.condition == AlertCondition.THRESHOLD_BELOW:
            triggered = metric_value < rule.threshold_value
            message = f"{rule.metric_name} ({metric_value:.3f}) below threshold ({rule.threshold_value})"
        
        elif rule.condition == AlertCondition.THRESHOLD_ABOVE:
            triggered = metric_value > rule.threshold_value
            message = f"{rule.metric_name} ({metric_value:.3f}) above threshold ({rule.threshold_value})"
        
        elif rule.condition == AlertCondition.STALENESS_EXCEEDED:
            triggered = metric_value > rule.threshold_value
            message = f"Data stale for {metric_value:.1f} days (threshold: {rule.threshold_value})"
        
        elif rule.condition == AlertCondition.PERCENTAGE_CHANGE:
            # Check for percentage change from historical average
            historical_avg = await self._get_historical_average(
                entity, rule.metric_name, session
            )
            if historical_avg:
                change_percent = ((metric_value - historical_avg) / historical_avg) * 100
                triggered = change_percent <= rule.threshold_value  # Negative threshold for drops
                message = f"{rule.metric_name} changed by {change_percent:.1f}% from historical average"
        
        if triggered:
            # Check cooldown
            if await self._is_in_cooldown(rule.rule_name, entity.entity_id, 
                                        rule.cooldown_minutes, session):
                return None
            
            return AlertTrigger(
                rule_name=rule.rule_name,
                entity_id=entity.entity_id,
                metric_value=metric_value,
                threshold_value=rule.threshold_value,
                severity=rule.severity,
                alert_type=rule.alert_type,
                message=message,
                metadata={
                    'entity_type': entity.entity_type,
                    'entity_data': entity.data,
                    'rule_description': rule.description,
                    'condition': rule.condition.value
                }
            )
        
        return None
    
    async def _evaluate_source_rule(self, rule: AlertRule, source: DataSource,
                                  metrics: Dict[str, float], session: AsyncSession) -> Optional[AlertTrigger]:
        """Evaluate a rule for a data source"""
        metric_value = metrics.get(rule.metric_name)
        if metric_value is None:
            return None
        
        triggered = False
        message = ""
        
        if rule.condition == AlertCondition.THRESHOLD_BELOW:
            triggered = metric_value < rule.threshold_value
            message = f"Source {rule.metric_name} ({metric_value:.3f}) below threshold ({rule.threshold_value})"
        
        elif rule.condition == AlertCondition.THRESHOLD_ABOVE:
            triggered = metric_value > rule.threshold_value
            message = f"Source {rule.metric_name} ({metric_value:.3f}) above threshold ({rule.threshold_value})"
        
        if triggered:
            # Check cooldown
            if await self._is_in_cooldown(rule.rule_name, f"source_{source.source_id}",
                                        rule.cooldown_minutes, session):
                return None
            
            return AlertTrigger(
                rule_name=rule.rule_name,
                entity_id=f"source_{source.source_id}",
                metric_value=metric_value,
                threshold_value=rule.threshold_value,
                severity=rule.severity,
                alert_type=rule.alert_type,
                message=message,
                metadata={
                    'source_name': source.name,
                    'source_url_pattern': source.url_pattern,
                    'rule_description': rule.description,
                    'condition': rule.condition.value
                }
            )
        
        return None
    
    async def _get_historical_average(self, entity: EntityRecord, metric_name: str,
                                    session: AsyncSession) -> Optional[float]:
        """Get historical average for a metric"""
        # Get assessments from last 30 days (excluding last 7 days for comparison)
        start_date = datetime.now(timezone.utc) - timedelta(days=30)
        end_date = datetime.now(timezone.utc) - timedelta(days=7)
        
        field_map = {
            'overall_quality_score': QualityAssessment.overall_score,
            'completeness_score': QualityAssessment.completeness_score,
            'consistency_score': QualityAssessment.consistency_score,
            'freshness_score': QualityAssessment.freshness_score,
            'confidence_score': QualityAssessment.confidence_score
        }
        
        if metric_name not in field_map:
            return None
        
        query = (
            select(func.avg(field_map[metric_name]))
            .where(
                and_(
                    QualityAssessment.entity_id == entity.id,
                    QualityAssessment.assessed_at >= start_date,
                    QualityAssessment.assessed_at <= end_date
                )
            )
        )
        
        result = await session.execute(query)
        return result.scalar()
    
    async def _is_in_cooldown(self, rule_name: str, entity_id: str,
                            cooldown_minutes: int, session: AsyncSession) -> bool:
        """Check if alert is in cooldown period"""
        cooldown_start = datetime.now(timezone.utc) - timedelta(minutes=cooldown_minutes)
        
        query = (
            select(func.count(QualityAlert.alert_id))
            .where(
                and_(
                    QualityAlert.rule_name == rule_name,
                    QualityAlert.entity_id == entity_id,
                    QualityAlert.triggered_at >= cooldown_start
                )
            )
        )
        
        count = (await session.execute(query)).scalar()
        return count > 0


class NotificationManager:
    """Manages alert notifications"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.email_config = self.config.get('email', {})
        self.webhook_config = self.config.get('webhook', {})
        self.enabled_channels = self.config.get('enabled_channels', ['log'])
    
    async def send_alert_notification(self, alert: QualityAlert,
                                    channels: List[str] = None) -> Dict[str, bool]:
        """Send alert notification through specified channels"""
        if not channels:
            channels = self.enabled_channels
        
        results = {}
        
        for channel in channels:
            try:
                if channel == 'email' and 'email' in self.enabled_channels:
                    results['email'] = await self._send_email_notification(alert)
                
                elif channel == 'webhook' and 'webhook' in self.enabled_channels:
                    results['webhook'] = await self._send_webhook_notification(alert)
                
                elif channel == 'log':
                    results['log'] = self._send_log_notification(alert)
                
                else:
                    logger.warning(f"Unknown notification channel: {channel}")
                    results[channel] = False
                    
            except Exception as e:
                logger.error(f"Error sending notification via {channel}: {e}")
                results[channel] = False
        
        return results
    
    async def _send_email_notification(self, alert: QualityAlert) -> bool:
        """Send email notification"""
        if not self.email_config:
            logger.warning("Email configuration not provided")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from_address']
            msg['To'] = ', '.join(self.email_config['to_addresses'])
            msg['Subject'] = f"Data Quality Alert: {alert.severity.upper()} - {alert.alert_type}"
            
            # Create email body
            body = self._format_email_body(alert)
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                if self.email_config.get('use_tls', True):
                    server.starttls()
                
                if self.email_config.get('username'):
                    server.login(
                        self.email_config['username'],
                        self.email_config['password']
                    )
                
                server.send_message(msg)
            
            logger.info(f"Email notification sent for alert {alert.alert_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False
    
    async def _send_webhook_notification(self, alert: QualityAlert) -> bool:
        """Send webhook notification"""
        import aiohttp
        
        if not self.webhook_config:
            logger.warning("Webhook configuration not provided")
            return False
        
        try:
            payload = {
                'alert_id': alert.alert_id,
                'alert_type': alert.alert_type,
                'severity': alert.severity,
                'entity_id': alert.entity_id,
                'message': alert.message,
                'triggered_at': alert.triggered_at.isoformat(),
                'metadata': alert.metadata
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_config['url'],
                    json=payload,
                    headers=self.webhook_config.get('headers', {}),
                    timeout=30
                ) as response:
                    if response.status == 200:
                        logger.info(f"Webhook notification sent for alert {alert.alert_id}")
                        return True
                    else:
                        logger.error(f"Webhook returned status {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
            return False
    
    def _send_log_notification(self, alert: QualityAlert) -> bool:
        """Send log notification"""
        log_level = {
            AlertSeverity.LOW: logging.INFO,
            AlertSeverity.MEDIUM: logging.WARNING,
            AlertSeverity.WARNING: logging.WARNING,
            AlertSeverity.HIGH: logging.ERROR,
            AlertSeverity.CRITICAL: logging.CRITICAL
        }.get(alert.severity, logging.WARNING)
        
        logger.log(
            log_level,
            f"QUALITY ALERT [{alert.severity}] {alert.alert_type}: {alert.message} "
            f"(Entity: {alert.entity_id}, Alert ID: {alert.alert_id})"
        )
        
        return True
    
    def _format_email_body(self, alert: QualityAlert) -> str:
        """Format email body for alert"""
        return f"""
        <html>
        <body>
            <h2>Data Quality Alert</h2>
            
            <h3>Alert Details</h3>
            <table border="1" cellpadding="5" cellspacing="0">
                <tr><td><strong>Alert ID</strong></td><td>{alert.alert_id}</td></tr>
                <tr><td><strong>Severity</strong></td><td style="color: {'red' if alert.severity == 'critical' else 'orange' if alert.severity == 'high' else 'gray'}">{alert.severity.upper()}</td></tr>
                <tr><td><strong>Type</strong></td><td>{alert.alert_type}</td></tr>
                <tr><td><strong>Entity ID</strong></td><td>{alert.entity_id}</td></tr>
                <tr><td><strong>Triggered At</strong></td><td>{alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</td></tr>
                <tr><td><strong>Rule</strong></td><td>{alert.rule_name or 'N/A'}</td></tr>
            </table>
            
            <h3>Message</h3>
            <p>{alert.message}</p>
            
            {f"<h3>Additional Details</h3><pre>{json.dumps(alert.metadata or {}, indent=2)}</pre>" if alert.metadata else ""}
            
            <hr>
            <p><em>This is an automated alert from the Data Quality Monitoring System.</em></p>
        </body>
        </html>
        """


class AlertManager:
    """Main manager for alert system"""
    
    def __init__(self, notification_config: Dict[str, Any] = None):
        self.evaluator = AlertEvaluator()
        self.notification_manager = NotificationManager(notification_config)
    
    async def process_entity_alerts(self, entity: EntityRecord,
                                  session: AsyncSession) -> List[QualityAlert]:
        """Process alerts for a single entity"""
        logger.debug(f"Processing alerts for entity {entity.entity_id}")
        
        triggers = await self.evaluator.evaluate_entity_alerts(entity, session)
        alerts = []
        
        for trigger in triggers:
            # Create alert record
            alert = QualityAlert(
                alert_type=trigger.alert_type,
                severity=trigger.severity,
                entity_id=entity.id,
                rule_name=trigger.rule_name,
                message=trigger.message,
                metadata=trigger.metadata,
                is_resolved=False
            )
            
            session.add(alert)
            await session.flush()  # Get alert ID
            
            # Send notifications
            await self.notification_manager.send_alert_notification(alert)
            
            alerts.append(alert)
            
            logger.info(f"Created alert {alert.alert_id} for entity {entity.entity_id}")
        
        await session.commit()
        return alerts
    
    async def process_source_alerts(self, source: DataSource,
                                  session: AsyncSession) -> List[QualityAlert]:
        """Process alerts for a data source"""
        logger.debug(f"Processing alerts for source {source.source_id}")
        
        triggers = await self.evaluator.evaluate_source_alerts(source, session)
        alerts = []
        
        for trigger in triggers:
            # Create alert record
            alert = QualityAlert(
                alert_type=trigger.alert_type,
                severity=trigger.severity,
                entity_id=None,  # Source-level alert
                rule_name=trigger.rule_name,
                message=trigger.message,
                metadata=trigger.metadata,
                is_resolved=False
            )
            
            session.add(alert)
            await session.flush()
            
            # Send notifications
            await self.notification_manager.send_alert_notification(alert)
            
            alerts.append(alert)
            
            logger.info(f"Created source alert {alert.alert_id} for source {source.source_id}")
        
        await session.commit()
        return alerts
    
    async def process_batch_alerts(self, session: AsyncSession,
                                 batch_size: int = 100) -> Dict[str, Any]:
        """Process alerts for a batch of entities and sources"""
        logger.info(f"Starting batch alert processing (batch size: {batch_size})")
        
        results = {
            'processed_entities': 0,
            'processed_sources': 0,
            'total_alerts': 0,
            'alerts_by_severity': {},
            'errors': []
        }
        
        try:
            # Process entity alerts
            entities_query = (
                select(EntityRecord)
                .where(EntityRecord.is_active == True)
                .order_by(EntityRecord.updated_at.desc())
                .limit(batch_size)
            )
            
            entities = (await session.execute(entities_query)).scalars().all()
            
            for entity in entities:
                try:
                    alerts = await self.process_entity_alerts(entity, session)
                    results['total_alerts'] += len(alerts)
                    
                    # Count by severity
                    for alert in alerts:
                        severity = alert.severity
                        results['alerts_by_severity'][severity] = results['alerts_by_severity'].get(severity, 0) + 1
                    
                    results['processed_entities'] += 1
                    
                except Exception as e:
                    logger.error(f"Error processing alerts for entity {entity.entity_id}: {e}")
                    results['errors'].append(f"Entity {entity.entity_id}: {str(e)}")
            
            # Process source alerts
            sources_query = (
                select(DataSource)
                .where(DataSource.is_active == True)
                .limit(20)  # Fewer sources to check
            )
            
            sources = (await session.execute(sources_query)).scalars().all()
            
            for source in sources:
                try:
                    alerts = await self.process_source_alerts(source, session)
                    results['total_alerts'] += len(alerts)
                    
                    # Count by severity
                    for alert in alerts:
                        severity = alert.severity
                        results['alerts_by_severity'][severity] = results['alerts_by_severity'].get(severity, 0) + 1
                    
                    results['processed_sources'] += 1
                    
                except Exception as e:
                    logger.error(f"Error processing alerts for source {source.source_id}: {e}")
                    results['errors'].append(f"Source {source.source_id}: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error in batch alert processing: {e}")
            results['errors'].append(f"Batch processing error: {str(e)}")
        
        logger.info(f"Batch alert processing complete: {results['total_alerts']} alerts generated")
        return results
    
    async def resolve_alert(self, alert_id: str, resolved_by: str,
                          resolution_notes: str, session: AsyncSession) -> QualityAlert:
        """Resolve an alert"""
        query = select(QualityAlert).where(QualityAlert.alert_id == alert_id)
        alert = (await session.execute(query)).scalar_one_or_none()
        
        if not alert:
            raise ValueError(f"Alert {alert_id} not found")
        
        alert.is_resolved = True
        alert.resolved_at = datetime.now(timezone.utc)
        alert.resolved_by = resolved_by
        alert.resolution_notes = resolution_notes
        
        await session.commit()
        
        logger.info(f"Alert {alert_id} resolved by {resolved_by}")
        return alert
    
    async def get_active_alerts(self, session: AsyncSession,
                              severity_filter: Optional[AlertSeverity] = None,
                              alert_type_filter: Optional[AlertType] = None,
                              limit: int = 100) -> List[Dict[str, Any]]:
        """Get active (unresolved) alerts"""
        query = (
            select(QualityAlert)
            .where(QualityAlert.is_resolved == False)
            .order_by(desc(QualityAlert.triggered_at))
            .limit(limit)
        )
        
        if severity_filter:
            query = query.where(QualityAlert.severity == severity_filter)
        
        if alert_type_filter:
            query = query.where(QualityAlert.alert_type == alert_type_filter)
        
        alerts = (await session.execute(query)).scalars().all()
        
        result = []
        for alert in alerts:
            result.append({
                'alert_id': alert.alert_id,
                'alert_type': alert.alert_type,
                'severity': alert.severity,
                'entity_id': alert.entity_id,
                'rule_name': alert.rule_name,
                'message': alert.message,
                'triggered_at': alert.triggered_at.isoformat(),
                'metadata': alert.metadata
            })
        
        return result


# Global alert manager instance
alert_manager = AlertManager()
