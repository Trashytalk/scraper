"""
Data Quality Management System
Provides comprehensive data quality monitoring, validation, and improvement
"""

import asyncio
import logging
import statistics
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict, Counter
from enum import Enum
import json
import re
import hashlib

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, update
from sqlalchemy.orm import selectinload

from ..database.config import get_async_session
from ..db.centralized_data import CentralizedDataRecord, DataAnalytics, DataDeduplication
from ..utils.performance import cached, performance_tracked


logger = logging.getLogger(__name__)


class QualityIssueType(Enum):
    """Types of data quality issues"""
    MISSING_CONTENT = "missing_content"
    DUPLICATE_CONTENT = "duplicate_content"
    INVALID_FORMAT = "invalid_format"
    LOW_COMPLETENESS = "low_completeness"
    SUSPICIOUS_PATTERN = "suspicious_pattern"
    ENCODING_ERROR = "encoding_error"
    BROKEN_LINK = "broken_link"
    OUTDATED_CONTENT = "outdated_content"
    SPAM_CONTENT = "spam_content"
    MALFORMED_DATA = "malformed_data"


class QualitySeverity(Enum):
    """Severity levels for quality issues"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class QualityIssue:
    """Data quality issue record"""
    issue_type: QualityIssueType
    severity: QualitySeverity
    description: str
    affected_field: Optional[str] = None
    suggested_fix: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    detected_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class QualityReport:
    """Comprehensive data quality report"""
    record_id: str
    overall_score: float
    completeness_score: float
    accuracy_score: float
    consistency_score: float
    timeliness_score: float
    issues: List[QualityIssue] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class QualityMetrics:
    """Aggregated quality metrics"""
    total_records: int = 0
    high_quality_records: int = 0
    medium_quality_records: int = 0
    low_quality_records: int = 0
    avg_quality_score: float = 0.0
    avg_completeness: float = 0.0
    duplicate_count: int = 0
    common_issues: Dict[str, int] = field(default_factory=dict)
    quality_trend: List[float] = field(default_factory=list)


class ContentAnalyzer:
    """Advanced content analysis for quality assessment"""
    
    def __init__(self):
        self.spam_indicators = [
            'click here', 'limited time', 'act now', 'free money',
            'make money fast', 'work from home', 'lose weight',
            'viagra', 'casino', 'lottery', 'congratulations'
        ]
        
        self.suspicious_patterns = [
            r'(.)\1{10,}',  # Repeated characters
            r'[A-Z]{20,}',  # Long uppercase sequences
            r'\d{15,}',     # Long number sequences
            r'[!@#$%^&*]{5,}',  # Excessive special characters
        ]
        
        self.encoding_patterns = [
            r'â€™',  # Common encoding issue
            r'Ã¡|Ã©|Ã­|Ã³|Ãº',  # Latin character encoding issues
            r'\ufffd',  # Unicode replacement character
        ]
    
    def analyze_content_quality(self, record: CentralizedDataRecord) -> QualityReport:
        """Perform comprehensive content quality analysis"""
        report = QualityReport(
            record_id=record.record_uuid,
            overall_score=0.0,
            completeness_score=0.0,
            accuracy_score=0.0,
            consistency_score=0.0,
            timeliness_score=0.0
        )
        
        # Analyze completeness
        self._analyze_completeness(record, report)
        
        # Analyze content accuracy
        self._analyze_accuracy(record, report)
        
        # Analyze consistency
        self._analyze_consistency(record, report)
        
        # Analyze timeliness
        self._analyze_timeliness(record, report)
        
        # Calculate overall score
        scores = [
            report.completeness_score,
            report.accuracy_score,
            report.consistency_score,
            report.timeliness_score
        ]
        report.overall_score = statistics.mean([s for s in scores if s > 0])
        
        # Generate recommendations
        self._generate_recommendations(record, report)
        
        return report
    
    def _analyze_completeness(self, record: CentralizedDataRecord, report: QualityReport):
        """Analyze data completeness"""
        essential_fields = [
            'title', 'extracted_text', 'source_url', 'data_type',
            'scraped_at', 'source_domain'
        ]
        
        optional_fields = [
            'summary', 'language', 'content_category', 'word_count',
            'content_published_at', 'link_count', 'image_count'
        ]
        
        # Check essential fields
        missing_essential = []
        for field in essential_fields:
            value = getattr(record, field, None)
            if not value or (isinstance(value, str) and not value.strip()):
                missing_essential.append(field)
        
        # Check optional fields
        filled_optional = sum(1 for field in optional_fields 
                            if getattr(record, field, None))
        
        # Calculate completeness score
        essential_score = ((len(essential_fields) - len(missing_essential)) / 
                          len(essential_fields)) * 70
        optional_score = (filled_optional / len(optional_fields)) * 30
        
        report.completeness_score = essential_score + optional_score
        
        # Add issues for missing essential fields
        for field in missing_essential:
            report.issues.append(QualityIssue(
                issue_type=QualityIssueType.MISSING_CONTENT,
                severity=QualitySeverity.HIGH,
                description=f"Missing essential field: {field}",
                affected_field=field,
                suggested_fix=f"Ensure {field} is properly extracted during scraping"
            ))
    
    def _analyze_accuracy(self, record: CentralizedDataRecord, report: QualityReport):
        """Analyze content accuracy"""
        accuracy_score = 100.0
        
        # Check for spam content
        if self._is_spam_content(record):
            accuracy_score -= 30
            report.issues.append(QualityIssue(
                issue_type=QualityIssueType.SPAM_CONTENT,
                severity=QualitySeverity.HIGH,
                description="Content appears to be spam or low-quality",
                suggested_fix="Review content filters and source quality"
            ))
        
        # Check for encoding errors
        if self._has_encoding_errors(record):
            accuracy_score -= 20
            report.issues.append(QualityIssue(
                issue_type=QualityIssueType.ENCODING_ERROR,
                severity=QualitySeverity.MEDIUM,
                description="Content contains encoding errors",
                suggested_fix="Review character encoding in scraping process"
            ))
        
        # Check for suspicious patterns
        suspicious_count = self._count_suspicious_patterns(record)
        if suspicious_count > 0:
            accuracy_score -= min(25, suspicious_count * 5)
            report.issues.append(QualityIssue(
                issue_type=QualityIssueType.SUSPICIOUS_PATTERN,
                severity=QualitySeverity.MEDIUM,
                description=f"Found {suspicious_count} suspicious content patterns",
                suggested_fix="Review content extraction and cleaning processes"
            ))
        
        # Check URL validity
        if not self._is_valid_url(record.source_url):
            accuracy_score -= 15
            report.issues.append(QualityIssue(
                issue_type=QualityIssueType.INVALID_FORMAT,
                severity=QualitySeverity.MEDIUM,
                description="Source URL format is invalid",
                affected_field="source_url",
                suggested_fix="Validate URL format before processing"
            ))
        
        report.accuracy_score = max(0.0, accuracy_score)
    
    def _analyze_consistency(self, record: CentralizedDataRecord, report: QualityReport):
        """Analyze data consistency"""
        consistency_score = 100.0
        
        # Check word count consistency
        if record.extracted_text and record.word_count:
            actual_words = len(record.extracted_text.split())
            if abs(actual_words - record.word_count) > actual_words * 0.2:  # 20% tolerance
                consistency_score -= 15
                report.issues.append(QualityIssue(
                    issue_type=QualityIssueType.MALFORMED_DATA,
                    severity=QualitySeverity.LOW,
                    description="Word count inconsistent with actual text",
                    affected_field="word_count",
                    suggested_fix="Recalculate word count during processing"
                ))
        
        # Check date consistency
        if (record.scraped_at and record.content_published_at and 
            record.content_published_at > record.scraped_at):
            consistency_score -= 10
            report.issues.append(QualityIssue(
                issue_type=QualityIssueType.INVALID_FORMAT,
                severity=QualitySeverity.MEDIUM,
                description="Published date is after scraped date",
                affected_field="content_published_at",
                suggested_fix="Validate date extraction logic"
            ))
        
        # Check quality score consistency
        if (record.data_quality_score and record.completeness_score and
            abs(record.data_quality_score - record.completeness_score) > 30):
            consistency_score -= 10
            report.issues.append(QualityIssue(
                issue_type=QualityIssueType.MALFORMED_DATA,
                severity=QualitySeverity.LOW,
                description="Quality scores are inconsistent",
                suggested_fix="Review quality calculation algorithms"
            ))
        
        # Check content length vs. quality
        if record.extracted_text:
            text_length = len(record.extracted_text)
            if text_length < 50 and record.data_quality_score > 70:
                consistency_score -= 20
                report.issues.append(QualityIssue(
                    issue_type=QualityIssueType.LOW_COMPLETENESS,
                    severity=QualitySeverity.MEDIUM,
                    description="High quality score for very short content",
                    suggested_fix="Review quality scoring for short content"
                ))
        
        report.consistency_score = max(0.0, consistency_score)
    
    def _analyze_timeliness(self, record: CentralizedDataRecord, report: QualityReport):
        """Analyze content timeliness"""
        timeliness_score = 100.0
        
        if not record.scraped_at:
            timeliness_score = 0.0
            return
        
        # Check if content is too old
        age_days = (datetime.utcnow() - record.scraped_at).days
        
        if age_days > 365:  # More than 1 year old
            timeliness_score -= 30
            report.issues.append(QualityIssue(
                issue_type=QualityIssueType.OUTDATED_CONTENT,
                severity=QualitySeverity.MEDIUM,
                description="Content is more than 1 year old",
                suggested_fix="Consider archiving or refreshing old content"
            ))
        elif age_days > 180:  # More than 6 months old
            timeliness_score -= 15
        elif age_days > 90:   # More than 3 months old
            timeliness_score -= 5
        
        # Check processing delay
        if record.centralized_at and record.scraped_at:
            processing_delay = (record.centralized_at - record.scraped_at).total_seconds()
            if processing_delay > 86400:  # More than 24 hours
                timeliness_score -= 10
                report.issues.append(QualityIssue(
                    issue_type=QualityIssueType.OUTDATED_CONTENT,
                    severity=QualitySeverity.LOW,
                    description="Long delay between scraping and processing",
                    suggested_fix="Optimize processing pipeline for faster turnaround"
                ))
        
        report.timeliness_score = max(0.0, timeliness_score)
    
    def _is_spam_content(self, record: CentralizedDataRecord) -> bool:
        """Check if content appears to be spam"""
        text = (record.extracted_text or '').lower()
        title = (record.title or '').lower()
        
        # Check for spam indicators
        spam_count = sum(1 for indicator in self.spam_indicators 
                        if indicator in text or indicator in title)
        
        return spam_count >= 2  # 2 or more spam indicators
    
    def _has_encoding_errors(self, record: CentralizedDataRecord) -> bool:
        """Check for character encoding errors"""
        text = record.extracted_text or ''
        title = record.title or ''
        
        for pattern in self.encoding_patterns:
            if re.search(pattern, text) or re.search(pattern, title):
                return True
        
        return False
    
    def _count_suspicious_patterns(self, record: CentralizedDataRecord) -> int:
        """Count suspicious content patterns"""
        text = record.extracted_text or ''
        count = 0
        
        for pattern in self.suspicious_patterns:
            matches = re.findall(pattern, text)
            count += len(matches)
        
        return count
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        if not url:
            return False
        
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return bool(url_pattern.match(url))
    
    def _generate_recommendations(self, record: CentralizedDataRecord, report: QualityReport):
        """Generate quality improvement recommendations"""
        # High-level recommendations based on overall score
        if report.overall_score < 50:
            report.recommendations.append("Overall quality is low - consider reviewing scraping sources and extraction processes")
        
        # Specific recommendations based on component scores
        if report.completeness_score < 70:
            report.recommendations.append("Improve data completeness by enhancing field extraction")
        
        if report.accuracy_score < 70:
            report.recommendations.append("Review content validation and filtering to improve accuracy")
        
        if report.consistency_score < 70:
            report.recommendations.append("Implement stricter data validation to ensure consistency")
        
        if report.timeliness_score < 70:
            report.recommendations.append("Optimize processing pipeline to reduce delays")
        
        # Issue-specific recommendations
        issue_types = [issue.issue_type for issue in report.issues]
        if QualityIssueType.DUPLICATE_CONTENT in issue_types:
            report.recommendations.append("Implement better deduplication strategies")
        
        if QualityIssueType.ENCODING_ERROR in issue_types:
            report.recommendations.append("Review character encoding settings in scraping configuration")


class DuplicationDetector:
    """Advanced duplicate content detection"""
    
    def __init__(self):
        self.similarity_threshold = 0.85
    
    async def detect_duplicates(self, record: CentralizedDataRecord) -> List[str]:
        """Detect duplicate records for given record"""
        duplicates = []
        
        try:
            async with get_async_session() as session:
                # First check exact content hash matches
                exact_matches = await session.execute(
                    select(CentralizedDataRecord.record_uuid)
                    .where(
                        and_(
                            CentralizedDataRecord.content_hash == record.content_hash,
                            CentralizedDataRecord.record_uuid != record.record_uuid
                        )
                    )
                )
                
                for match in exact_matches.scalars():
                    duplicates.append(match)
                
                # Check for near-duplicates using text similarity
                if record.extracted_text and len(record.extracted_text) > 100:
                    similar_records = await self._find_similar_content(session, record)
                    duplicates.extend(similar_records)
                
        except Exception as e:
            logger.error(f"Duplicate detection failed for {record.record_uuid}: {e}")
        
        return list(set(duplicates))  # Remove duplicates from the duplicates list
    
    async def _find_similar_content(self, session: AsyncSession, record: CentralizedDataRecord) -> List[str]:
        """Find records with similar content using text similarity"""
        similar_records = []
        
        try:
            # Get records from same domain with similar word count
            word_count_range = 0.2  # 20% tolerance
            min_words = record.word_count * (1 - word_count_range)
            max_words = record.word_count * (1 + word_count_range)
            
            candidates = await session.execute(
                select(CentralizedDataRecord)
                .where(
                    and_(
                        CentralizedDataRecord.source_domain == record.source_domain,
                        CentralizedDataRecord.word_count.between(min_words, max_words),
                        CentralizedDataRecord.record_uuid != record.record_uuid,
                        CentralizedDataRecord.extracted_text.isnot(None)
                    )
                )
                .limit(50)  # Limit to prevent performance issues
            )
            
            # Calculate similarity for each candidate
            record_text = self._normalize_text(record.extracted_text)
            
            for candidate in candidates.scalars():
                candidate_text = self._normalize_text(candidate.extracted_text)
                similarity = self._calculate_similarity(record_text, candidate_text)
                
                if similarity >= self.similarity_threshold:
                    similar_records.append(candidate.record_uuid)
                    logger.debug(f"Found similar content: {similarity:.2f} similarity")
        
        except Exception as e:
            logger.error(f"Similar content detection failed: {e}")
        
        return similar_records
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for similarity comparison"""
        if not text:
            return ""
        
        # Convert to lowercase, remove extra whitespace, remove punctuation
        normalized = re.sub(r'[^\w\s]', '', text.lower())
        normalized = re.sub(r'\s+', ' ', normalized)
        return normalized.strip()
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using Jaccard similarity"""
        if not text1 or not text2:
            return 0.0
        
        # Split into words
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    async def mark_duplicates(self, canonical_record_uuid: str, duplicate_uuids: List[str]):
        """Mark records as duplicates in the database"""
        try:
            async with get_async_session() as session:
                # Get canonical record
                canonical_result = await session.execute(
                    select(CentralizedDataRecord).where(
                        CentralizedDataRecord.record_uuid == canonical_record_uuid
                    )
                )
                canonical_record = canonical_result.scalar_one_or_none()
                
                if not canonical_record:
                    logger.error(f"Canonical record not found: {canonical_record_uuid}")
                    return
                
                # Create deduplication record
                dedup_record = DataDeduplication(
                    content_hash=canonical_record.content_hash,
                    canonical_record_id=canonical_record.id,
                    duplicate_record_ids=duplicate_uuids,
                    similarity_score=int(self.similarity_threshold * 100),
                    dedup_method="content_similarity"
                )
                
                session.add(dedup_record)
                
                # Mark duplicate records
                for duplicate_uuid in duplicate_uuids:
                    await session.execute(
                        update(CentralizedDataRecord)
                        .where(CentralizedDataRecord.record_uuid == duplicate_uuid)
                        .values(validation_status="duplicate")
                    )
                
                await session.commit()
                logger.info(f"Marked {len(duplicate_uuids)} records as duplicates of {canonical_record_uuid}")
                
        except Exception as e:
            logger.error(f"Failed to mark duplicates: {e}")


class QualityAnalytics:
    """Quality analytics and trend analysis"""
    
    @cached(ttl=1800)  # Cache for 30 minutes
    async def get_quality_metrics(self, days: int = 30) -> QualityMetrics:
        """Get aggregated quality metrics"""
        metrics = QualityMetrics()
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            async with get_async_session() as session:
                # Get basic counts
                result = await session.execute(
                    select(
                        func.count(CentralizedDataRecord.id),
                        func.avg(CentralizedDataRecord.data_quality_score),
                        func.avg(CentralizedDataRecord.completeness_score)
                    )
                    .where(CentralizedDataRecord.centralized_at >= cutoff_date)
                )
                
                counts = result.first()
                if counts:
                    metrics.total_records = counts[0] or 0
                    metrics.avg_quality_score = counts[1] or 0.0
                    metrics.avg_completeness = counts[2] or 0.0
                
                # Get quality distribution
                quality_distribution = await session.execute(
                    select(
                        func.count(CentralizedDataRecord.id).label('count'),
                        func.case(
                            (CentralizedDataRecord.data_quality_score >= 80, 'high'),
                            (CentralizedDataRecord.data_quality_score >= 60, 'medium'),
                            else_='low'
                        ).label('quality_tier')
                    )
                    .where(CentralizedDataRecord.centralized_at >= cutoff_date)
                    .group_by('quality_tier')
                )
                
                for row in quality_distribution:
                    if row.quality_tier == 'high':
                        metrics.high_quality_records = row.count
                    elif row.quality_tier == 'medium':
                        metrics.medium_quality_records = row.count
                    else:
                        metrics.low_quality_records = row.count
                
                # Get duplicate count
                duplicate_count = await session.execute(
                    select(func.count(DataDeduplication.id))
                    .where(DataDeduplication.created_at >= cutoff_date)
                )
                metrics.duplicate_count = duplicate_count.scalar() or 0
                
                # Get quality trend (daily averages for the period)
                daily_quality = await session.execute(
                    select(
                        func.date(CentralizedDataRecord.centralized_at).label('date'),
                        func.avg(CentralizedDataRecord.data_quality_score).label('avg_quality')
                    )
                    .where(CentralizedDataRecord.centralized_at >= cutoff_date)
                    .group_by(func.date(CentralizedDataRecord.centralized_at))
                    .order_by('date')
                )
                
                metrics.quality_trend = [row.avg_quality for row in daily_quality if row.avg_quality]
                
        except Exception as e:
            logger.error(f"Failed to get quality metrics: {e}")
        
        return metrics
    
    async def get_common_issues(self, days: int = 30) -> Dict[str, int]:
        """Get most common quality issues"""
        issues = defaultdict(int)
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            async with get_async_session() as session:
                # Get records with validation notes
                records = await session.execute(
                    select(CentralizedDataRecord.validation_notes)
                    .where(
                        and_(
                            CentralizedDataRecord.centralized_at >= cutoff_date,
                            CentralizedDataRecord.validation_notes.isnot(None)
                        )
                    )
                )
                
                for record in records.scalars():
                    if record:
                        try:
                            validation_data = json.loads(record)
                            for error in validation_data.get('errors', []):
                                # Extract issue type from error message
                                if 'missing' in error.lower():
                                    issues['missing_content'] += 1
                                elif 'invalid' in error.lower():
                                    issues['invalid_format'] += 1
                                elif 'quality' in error.lower():
                                    issues['low_quality'] += 1
                                else:
                                    issues['other'] += 1
                        except:
                            continue
                            
        except Exception as e:
            logger.error(f"Failed to get common issues: {e}")
        
        return dict(issues)


class QualityManager:
    """Main quality management service"""
    
    def __init__(self):
        self.content_analyzer = ContentAnalyzer()
        self.duplication_detector = DuplicationDetector()
        self.quality_analytics = QualityAnalytics()
    
    async def assess_record_quality(self, record_uuid: str) -> QualityReport:
        """Assess quality of a specific record"""
        try:
            async with get_async_session() as session:
                result = await session.execute(
                    select(CentralizedDataRecord).where(
                        CentralizedDataRecord.record_uuid == record_uuid
                    )
                )
                record = result.scalar_one_or_none()
                
                if not record:
                    raise ValueError(f"Record not found: {record_uuid}")
                
                # Perform quality analysis
                report = self.content_analyzer.analyze_content_quality(record)
                
                # Check for duplicates
                duplicates = await self.duplication_detector.detect_duplicates(record)
                if duplicates:
                    report.issues.append(QualityIssue(
                        issue_type=QualityIssueType.DUPLICATE_CONTENT,
                        severity=QualitySeverity.MEDIUM,
                        description=f"Found {len(duplicates)} potential duplicates",
                        metadata={'duplicate_uuids': duplicates}
                    ))
                
                return report
                
        except Exception as e:
            logger.error(f"Quality assessment failed for {record_uuid}: {e}")
            raise
    
    async def batch_quality_assessment(self, limit: int = 100) -> List[QualityReport]:
        """Perform quality assessment on a batch of records"""
        reports = []
        
        try:
            async with get_async_session() as session:
                # Get records that need quality assessment
                result = await session.execute(
                    select(CentralizedDataRecord)
                    .where(
                        or_(
                            CentralizedDataRecord.validation_status == "pending",
                            CentralizedDataRecord.data_quality_score == 0
                        )
                    )
                    .limit(limit)
                )
                
                records = result.scalars().all()
                
                for record in records:
                    try:
                        report = self.content_analyzer.analyze_content_quality(record)
                        reports.append(report)
                        
                        # Update record with quality scores
                        record.data_quality_score = report.overall_score
                        record.completeness_score = report.completeness_score
                        record.validation_status = "valid" if report.overall_score >= 50 else "invalid"
                        
                        # Store validation notes
                        validation_data = {
                            'issues': [
                                {
                                    'type': issue.issue_type.value,
                                    'severity': issue.severity.value,
                                    'description': issue.description
                                }
                                for issue in report.issues
                            ],
                            'recommendations': report.recommendations,
                            'assessed_at': datetime.utcnow().isoformat()
                        }
                        record.validation_notes = json.dumps(validation_data)
                        
                    except Exception as e:
                        logger.error(f"Failed to assess record {record.record_uuid}: {e}")
                        continue
                
                await session.commit()
                logger.info(f"Completed quality assessment for {len(reports)} records")
                
        except Exception as e:
            logger.error(f"Batch quality assessment failed: {e}")
        
        return reports
    
    async def cleanup_duplicates(self, batch_size: int = 50) -> Dict[str, Any]:
        """Clean up duplicate records"""
        cleanup_stats = {
            'processed_groups': 0,
            'duplicates_marked': 0,
            'errors': 0
        }
        
        try:
            async with get_async_session() as session:
                # Find records with same content hash
                duplicate_groups = await session.execute(
                    select(
                        CentralizedDataRecord.content_hash,
                        func.count(CentralizedDataRecord.id).label('count'),
                        func.min(CentralizedDataRecord.centralized_at).label('earliest_date')
                    )
                    .group_by(CentralizedDataRecord.content_hash)
                    .having(func.count(CentralizedDataRecord.id) > 1)
                    .limit(batch_size)
                )
                
                for group in duplicate_groups:
                    try:
                        # Get all records in this duplicate group
                        records_result = await session.execute(
                            select(CentralizedDataRecord)
                            .where(CentralizedDataRecord.content_hash == group.content_hash)
                            .order_by(CentralizedDataRecord.centralized_at)
                        )
                        
                        records = list(records_result.scalars())
                        if len(records) <= 1:
                            continue
                        
                        # First record is canonical, rest are duplicates
                        canonical = records[0]
                        duplicates = records[1:]
                        
                        duplicate_uuids = [r.record_uuid for r in duplicates]
                        
                        # Mark duplicates
                        await self.duplication_detector.mark_duplicates(
                            canonical.record_uuid, 
                            duplicate_uuids
                        )
                        
                        cleanup_stats['processed_groups'] += 1
                        cleanup_stats['duplicates_marked'] += len(duplicates)
                        
                    except Exception as e:
                        logger.error(f"Failed to cleanup duplicate group {group.content_hash}: {e}")
                        cleanup_stats['errors'] += 1
                        continue
                        
        except Exception as e:
            logger.error(f"Duplicate cleanup failed: {e}")
            cleanup_stats['errors'] += 1
        
        return cleanup_stats
    
    async def get_quality_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive quality data for dashboard"""
        try:
            # Get quality metrics
            metrics = await self.quality_analytics.get_quality_metrics()
            
            # Get common issues
            common_issues = await self.quality_analytics.get_common_issues()
            
            # Calculate quality distribution
            total_records = metrics.total_records
            quality_distribution = {
                'high_quality': {
                    'count': metrics.high_quality_records,
                    'percentage': (metrics.high_quality_records / total_records * 100) if total_records > 0 else 0
                },
                'medium_quality': {
                    'count': metrics.medium_quality_records,
                    'percentage': (metrics.medium_quality_records / total_records * 100) if total_records > 0 else 0
                },
                'low_quality': {
                    'count': metrics.low_quality_records,
                    'percentage': (metrics.low_quality_records / total_records * 100) if total_records > 0 else 0
                }
            }
            
            return {
                'overall_metrics': {
                    'total_records': total_records,
                    'avg_quality_score': round(metrics.avg_quality_score, 2),
                    'avg_completeness': round(metrics.avg_completeness, 2),
                    'duplicate_count': metrics.duplicate_count
                },
                'quality_distribution': quality_distribution,
                'quality_trend': metrics.quality_trend,
                'common_issues': common_issues,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get quality dashboard data: {e}")
            return {}


# Global quality manager instance
quality_manager = QualityManager()


# Convenience functions for external use
async def assess_data_quality(record_uuid: str) -> QualityReport:
    """Assess quality of a specific record"""
    return await quality_manager.assess_record_quality(record_uuid)


async def run_quality_batch_assessment(limit: int = 100) -> List[QualityReport]:
    """Run batch quality assessment"""
    return await quality_manager.batch_quality_assessment(limit)


async def cleanup_duplicate_records(batch_size: int = 50) -> Dict[str, Any]:
    """Clean up duplicate records"""
    return await quality_manager.cleanup_duplicates(batch_size)


async def get_quality_metrics(days: int = 30) -> QualityMetrics:
    """Get quality metrics for specified period"""
    return await quality_manager.quality_analytics.get_quality_metrics(days)
