"""
Data Quality Assessment Engine

Comprehensive system for evaluating, scoring, and monitoring data quality
across all business intelligence entities and fields.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
import statistics
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from .quality_models import (
    EntityRecord,
    QualityAssessment,
    DataSource,
    ProvenanceRecord,
    QualityStatus,
    ConfidenceLevel,
)

logger = logging.getLogger(__name__)


@dataclass
class QualityMetric:
    """Individual quality metric result"""

    name: str
    score: float  # 0-1
    weight: float
    details: Dict[str, Any]
    issues: List[str]
    recommendations: List[str]


@dataclass
class QualityAssessmentResult:
    """Complete quality assessment result"""

    entity_id: str
    overall_score: float
    completeness_score: float
    consistency_score: float
    freshness_score: float
    confidence_score: float
    quality_status: QualityStatus
    confidence_level: ConfidenceLevel
    metrics: List[QualityMetric]
    issues: List[str]
    recommendations: List[str]


class QualityAssessor(ABC):
    """Base class for quality assessors"""

    def __init__(self, name: str, weight: float = 1.0):
        self.name = name
        self.weight = weight

    @abstractmethod
    async def assess(
        self, entity: EntityRecord, session: AsyncSession
    ) -> QualityMetric:
        """Assess quality for an entity"""
        pass


class CompletenessAssessor(QualityAssessor):
    """Assesses data completeness"""

    def __init__(self):
        super().__init__("completeness", weight=0.3)

        # Define required fields by entity type
        self.required_fields = {
            "company": ["name", "registration_id", "address", "status"],
            "person": ["name", "role"],
            "address": ["street", "city", "country"],
            "contact": ["type", "value"],
            "financial": ["amount", "currency", "date"],
        }

        # Define optional but valuable fields
        self.optional_fields = {
            "company": [
                "phone",
                "email",
                "website",
                "industry",
                "employees",
                "revenue",
            ],
            "person": ["phone", "email", "nationality", "birth_date"],
            "address": ["postal_code", "coordinates"],
            "contact": ["verified", "primary"],
            "financial": ["description", "category"],
        }

    async def assess(
        self, entity: EntityRecord, session: AsyncSession
    ) -> QualityMetric:
        """Assess completeness of entity data"""
        entity_type = entity.entity_type
        data = entity.data

        required = self.required_fields.get(entity_type, [])
        optional = self.optional_fields.get(entity_type, [])

        # Count present required fields
        present_required = sum(
            1 for field in required if self._is_field_present(data, field)
        )
        required_score = present_required / len(required) if required else 1.0

        # Count present optional fields
        present_optional = sum(
            1 for field in optional if self._is_field_present(data, field)
        )
        optional_score = present_optional / len(optional) if optional else 0.0

        # Weighted score (required fields are more important)
        overall_score = (required_score * 0.8) + (optional_score * 0.2)

        # Identify missing critical fields
        missing_required = [
            field for field in required if not self._is_field_present(data, field)
        ]
        missing_optional = [
            field for field in optional if not self._is_field_present(data, field)
        ]

        issues = []
        recommendations = []

        if missing_required:
            issues.append(f"Missing required fields: {', '.join(missing_required)}")
            recommendations.append(
                f"Collect missing required data: {', '.join(missing_required)}"
            )

        if (
            len(missing_optional) > len(optional) * 0.5
        ):  # More than 50% optional fields missing
            recommendations.append(
                f"Consider collecting optional data for better insights: {', '.join(missing_optional[:3])}..."
            )

        return QualityMetric(
            name=self.name,
            score=overall_score,
            weight=self.weight,
            details={
                "required_fields": required,
                "optional_fields": optional,
                "present_required": present_required,
                "present_optional": present_optional,
                "required_score": required_score,
                "optional_score": optional_score,
                "missing_required": missing_required,
                "missing_optional": missing_optional,
            },
            issues=issues,
            recommendations=recommendations,
        )

    def _is_field_present(self, data: Dict[str, Any], field: str) -> bool:
        """Check if a field is present and has a meaningful value"""
        if field not in data:
            return False

        value = data[field]

        # Check for empty or null values
        if value is None or value == "" or value == []:
            return False

        # Check for placeholder values
        placeholders = {
            "n/a",
            "na",
            "null",
            "unknown",
            "not available",
            "tbd",
            "pending",
        }
        if isinstance(value, str) and value.lower().strip() in placeholders:
            return False

        return True


class ConsistencyAssessor(QualityAssessor):
    """Assesses data consistency across sources and time"""

    def __init__(self):
        super().__init__("consistency", weight=0.25)

    async def assess(
        self, entity: EntityRecord, session: AsyncSession
    ) -> QualityMetric:
        """Assess consistency of entity data"""
        # Get all provenance records for this entity
        provenance_query = (
            select(ProvenanceRecord)
            .where(ProvenanceRecord.entity_id == entity.id)
            .options(selectinload(ProvenanceRecord.raw_record))
        )

        provenance_records = (await session.execute(provenance_query)).scalars().all()

        # Group by field to check for conflicts
        field_sources = defaultdict(list)
        for prov in provenance_records:
            field_sources[prov.field_name].append(
                {
                    "value": prov.field_value,
                    "source_url": prov.source_url,
                    "extracted_at": prov.extracted_at,
                    "confidence": prov.extraction_confidence,
                }
            )

        consistency_scores = []
        issues = []
        recommendations = []

        for field, sources in field_sources.items():
            if len(sources) <= 1:
                consistency_scores.append(1.0)  # Single source = consistent
                continue

            # Check for value conflicts
            values = [s["value"] for s in sources if s["value"]]
            unique_values = set(values)

            if len(unique_values) == 1:
                # All sources agree
                consistency_scores.append(1.0)
            elif len(unique_values) <= len(values) * 0.3:  # Minor conflicts
                consistency_scores.append(0.7)
                issues.append(
                    f"Minor value conflicts in field '{field}': {list(unique_values)[:3]}"
                )
            else:
                # Major conflicts
                consistency_scores.append(0.3)
                issues.append(
                    f"Major value conflicts in field '{field}': {list(unique_values)[:3]}"
                )
                recommendations.append(
                    f"Review conflicting values for field '{field}' and determine canonical value"
                )

        # Check temporal consistency (values changing unexpectedly)
        temporal_score = await self._assess_temporal_consistency(entity, session)
        consistency_scores.append(temporal_score)

        overall_score = (
            statistics.mean(consistency_scores) if consistency_scores else 0.0
        )

        return QualityMetric(
            name=self.name,
            score=overall_score,
            weight=self.weight,
            details={
                "field_conflicts": len([s for s in consistency_scores if s < 1.0]),
                "temporal_consistency": temporal_score,
                "sources_count": len(provenance_records),
            },
            issues=issues,
            recommendations=recommendations,
        )

    async def _assess_temporal_consistency(
        self, entity: EntityRecord, session: AsyncSession
    ) -> float:
        """Assess consistency over time"""
        # This would check for unexpected changes in stable fields
        # For now, return a baseline score
        return 0.8


class FreshnessAssessor(QualityAssessor):
    """Assesses data freshness and staleness"""

    def __init__(self):
        super().__init__("freshness", weight=0.2)

        # Define freshness expectations by entity type (in days)
        self.freshness_expectations = {
            "company": 30,  # Company data should be updated monthly
            "person": 90,  # Person data can be older
            "address": 180,  # Address data changes less frequently
            "contact": 30,  # Contact info should be current
            "financial": 7,  # Financial data should be very current
        }

    async def assess(
        self, entity: EntityRecord, session: AsyncSession
    ) -> QualityMetric:
        """Assess freshness of entity data"""
        now = datetime.now(timezone.utc)
        entity_type = entity.entity_type

        # Get the most recent update time
        last_update = entity.updated_at or entity.created_at
        age_days = (now - last_update).total_seconds() / 86400

        # Get expected freshness for this entity type
        expected_freshness = self.freshness_expectations.get(entity_type, 30)

        # Calculate freshness score
        if age_days <= expected_freshness:
            freshness_score = 1.0
        elif age_days <= expected_freshness * 2:
            freshness_score = 0.7
        elif age_days <= expected_freshness * 4:
            freshness_score = 0.4
        else:
            freshness_score = 0.1

        # Check source-level freshness
        source_freshness = await self._assess_source_freshness(entity, session)

        # Combined score
        overall_score = (freshness_score + source_freshness) / 2

        issues = []
        recommendations = []

        if age_days > expected_freshness:
            if age_days > expected_freshness * 4:
                issues.append(
                    f"Data is very stale: {age_days:.1f} days old (expected < {expected_freshness} days)"
                )
                recommendations.append(
                    "Urgent: Update this entity's data from original sources"
                )
            elif age_days > expected_freshness * 2:
                issues.append(
                    f"Data is stale: {age_days:.1f} days old (expected < {expected_freshness} days)"
                )
                recommendations.append("Schedule data refresh from original sources")
            else:
                recommendations.append("Consider refreshing data soon")

        return QualityMetric(
            name=self.name,
            score=overall_score,
            weight=self.weight,
            details={
                "age_days": age_days,
                "expected_freshness_days": expected_freshness,
                "last_update": last_update.isoformat(),
                "source_freshness_score": source_freshness,
            },
            issues=issues,
            recommendations=recommendations,
        )

    async def _assess_source_freshness(
        self, entity: EntityRecord, session: AsyncSession
    ) -> float:
        """Assess freshness of underlying sources"""
        # Get all data sources for this entity
        sources_query = (
            select(DataSource)
            .join(
                ProvenanceRecord,
                DataSource.id
                == ProvenanceRecord.raw_record.has(
                    ProvenanceRecord.entity_id == entity.id
                ),
            )
            .distinct()
        )

        try:
            sources = (await session.execute(sources_query)).scalars().all()

            if not sources:
                return 0.5  # No source info available

            freshness_scores = []
            for source in sources:
                if source.last_successful_access:
                    age = (
                        datetime.now(timezone.utc) - source.last_successful_access
                    ).total_seconds() / 86400
                    if age <= source.update_frequency_hours / 24:
                        freshness_scores.append(1.0)
                    elif age <= (source.update_frequency_hours / 24) * 2:
                        freshness_scores.append(0.7)
                    else:
                        freshness_scores.append(0.3)
                else:
                    freshness_scores.append(0.1)  # Never accessed

            return statistics.mean(freshness_scores)

        except Exception as e:
            logger.error(f"Error assessing source freshness: {e}")
            return 0.5


class ConfidenceAssessor(QualityAssessor):
    """Assesses confidence based on source reliability and extraction quality"""

    def __init__(self):
        super().__init__("confidence", weight=0.25)

    async def assess(
        self, entity: EntityRecord, session: AsyncSession
    ) -> QualityMetric:
        """Assess confidence in entity data"""
        # Get all provenance records with source information
        provenance_query = (
            select(ProvenanceRecord)
            .where(ProvenanceRecord.entity_id == entity.id)
            .options(selectinload(ProvenanceRecord.raw_record).selectinload(DataSource))
        )

        provenance_records = (await session.execute(provenance_query)).scalars().all()

        if not provenance_records:
            return QualityMetric(
                name=self.name,
                score=0.1,
                weight=self.weight,
                details={"reason": "No provenance information available"},
                issues=["No source tracking available"],
                recommendations=["Implement proper provenance tracking"],
            )

        confidence_scores = []
        source_scores = []
        extraction_scores = []

        for prov in provenance_records:
            # Source reliability score
            if prov.raw_record and prov.raw_record.source:
                source_reliability = prov.raw_record.source.reliability_score
                source_scores.append(source_reliability)

            # Extraction confidence
            extraction_confidence = prov.extraction_confidence
            extraction_scores.append(extraction_confidence)

            # Combined score for this field
            field_confidence = (source_reliability + extraction_confidence) / 2
            confidence_scores.append(field_confidence)

        # Calculate overall confidence
        avg_source_score = statistics.mean(source_scores) if source_scores else 0.5
        avg_extraction_score = (
            statistics.mean(extraction_scores) if extraction_scores else 0.5
        )
        overall_confidence = (
            statistics.mean(confidence_scores) if confidence_scores else 0.1
        )

        # Source diversity bonus
        unique_sources = len(
            set(
                prov.raw_record.source.source_id
                for prov in provenance_records
                if prov.raw_record
            )
        )
        diversity_bonus = min(
            0.1, unique_sources * 0.02
        )  # Up to 10% bonus for multiple sources

        final_score = min(1.0, overall_confidence + diversity_bonus)

        issues = []
        recommendations = []

        if avg_source_score < 0.5:
            issues.append("Low source reliability scores")
            recommendations.append("Verify data with additional high-quality sources")

        if avg_extraction_score < 0.5:
            issues.append("Low extraction confidence")
            recommendations.append("Review and improve data extraction methods")

        if unique_sources == 1:
            recommendations.append(
                "Cross-verify with additional sources to increase confidence"
            )

        return QualityMetric(
            name=self.name,
            score=final_score,
            weight=self.weight,
            details={
                "source_reliability_avg": avg_source_score,
                "extraction_confidence_avg": avg_extraction_score,
                "unique_sources": unique_sources,
                "diversity_bonus": diversity_bonus,
                "total_provenance_records": len(provenance_records),
            },
            issues=issues,
            recommendations=recommendations,
        )


class DataQualityEngine:
    """Main engine for assessing and monitoring data quality"""

    def __init__(self):
        self.assessors = [
            CompletenessAssessor(),
            ConsistencyAssessor(),
            FreshnessAssessor(),
            ConfidenceAssessor(),
        ]

        # Quality thresholds
        self.quality_thresholds = {
            QualityStatus.EXCELLENT: 0.9,
            QualityStatus.GOOD: 0.75,
            QualityStatus.FAIR: 0.5,
            QualityStatus.POOR: 0.25,
            QualityStatus.CRITICAL: 0.0,
        }

        self.confidence_thresholds = {
            ConfidenceLevel.VERY_HIGH: 0.9,
            ConfidenceLevel.HIGH: 0.75,
            ConfidenceLevel.MEDIUM: 0.5,
            ConfidenceLevel.LOW: 0.25,
            ConfidenceLevel.VERY_LOW: 0.0,
        }

    async def assess_entity(
        self, entity: EntityRecord, session: AsyncSession
    ) -> QualityAssessmentResult:
        """Perform comprehensive quality assessment for an entity"""
        logger.info(f"Assessing quality for entity {entity.entity_id}")

        metrics = []

        # Run all assessors
        for assessor in self.assessors:
            try:
                metric = await assessor.assess(entity, session)
                metrics.append(metric)
            except Exception as e:
                logger.error(f"Error in {assessor.name} assessment: {e}")
                # Create error metric
                error_metric = QualityMetric(
                    name=assessor.name,
                    score=0.0,
                    weight=assessor.weight,
                    details={"error": str(e)},
                    issues=[f"Assessment failed: {str(e)}"],
                    recommendations=[f"Fix {assessor.name} assessment"],
                )
                metrics.append(error_metric)

        # Calculate weighted overall score
        total_weight = sum(m.weight for m in metrics)
        if total_weight > 0:
            overall_score = sum(m.score * m.weight for m in metrics) / total_weight
        else:
            overall_score = 0.0

        # Extract individual scores
        completeness_score = next(
            (m.score for m in metrics if m.name == "completeness"), 0.0
        )
        consistency_score = next(
            (m.score for m in metrics if m.name == "consistency"), 0.0
        )
        freshness_score = next((m.score for m in metrics if m.name == "freshness"), 0.0)
        confidence_score = next(
            (m.score for m in metrics if m.name == "confidence"), 0.0
        )

        # Determine quality status
        quality_status = self._determine_quality_status(overall_score)
        confidence_level = self._determine_confidence_level(confidence_score)

        # Collect all issues and recommendations
        all_issues = []
        all_recommendations = []
        for metric in metrics:
            all_issues.extend(metric.issues)
            all_recommendations.extend(metric.recommendations)

        return QualityAssessmentResult(
            entity_id=entity.entity_id,
            overall_score=overall_score,
            completeness_score=completeness_score,
            consistency_score=consistency_score,
            freshness_score=freshness_score,
            confidence_score=confidence_score,
            quality_status=quality_status,
            confidence_level=confidence_level,
            metrics=metrics,
            issues=all_issues,
            recommendations=all_recommendations,
        )

    async def store_assessment(
        self,
        assessment: QualityAssessmentResult,
        entity: EntityRecord,
        session: AsyncSession,
    ) -> None:
        """Store assessment results in database"""
        # Update entity quality scores
        entity.overall_quality_score = assessment.overall_score
        entity.completeness_score = assessment.completeness_score
        entity.consistency_score = assessment.consistency_score
        entity.freshness_score = assessment.freshness_score
        entity.confidence_score = assessment.confidence_score
        entity.quality_status = assessment.quality_status
        entity.confidence_level = assessment.confidence_level
        entity.quality_issues = assessment.issues
        entity.has_issues = len(assessment.issues) > 0

        # Store detailed assessment records
        for metric in assessment.metrics:
            quality_assessment = QualityAssessment(
                entity_id=entity.id,
                assessment_type=metric.name,
                score=metric.score,
                weight=metric.weight,
                criteria={"type": metric.name},
                results=metric.details,
                issues_found=metric.issues,
                recommendations=metric.recommendations,
                assessor="system",
            )
            session.add(quality_assessment)

        await session.commit()
        logger.info(
            f"Stored assessment for entity {entity.entity_id} (score: {assessment.overall_score:.3f})"
        )

    async def batch_assess_entities(
        self, entity_ids: List[str], session: AsyncSession
    ) -> List[QualityAssessmentResult]:
        """Assess multiple entities in batch"""
        results = []

        for entity_id in entity_ids:
            try:
                # Get entity
                entity_query = select(EntityRecord).where(
                    EntityRecord.entity_id == entity_id
                )
                entity = (await session.execute(entity_query)).scalar_one_or_none()

                if not entity:
                    logger.warning(f"Entity {entity_id} not found")
                    continue

                # Assess and store
                assessment = await self.assess_entity(entity, session)
                await self.store_assessment(assessment, entity, session)
                results.append(assessment)

            except Exception as e:
                logger.error(f"Error assessing entity {entity_id}: {e}")

        return results

    async def assess_all_entities(
        self, session: AsyncSession, batch_size: int = 100
    ) -> Dict[str, Any]:
        """Assess all entities in the database"""
        logger.info("Starting full database quality assessment")

        # Count total entities
        count_query = select(func.count(EntityRecord.id)).where(
            EntityRecord.is_active == True
        )
        total_count = (await session.execute(count_query)).scalar()

        processed = 0
        results = {
            "total_entities": total_count,
            "processed": 0,
            "excellent": 0,
            "good": 0,
            "fair": 0,
            "poor": 0,
            "critical": 0,
            "errors": [],
        }

        # Process in batches
        offset = 0
        while offset < total_count:
            try:
                # Get batch of entities
                entities_query = (
                    select(EntityRecord)
                    .where(EntityRecord.is_active == True)
                    .offset(offset)
                    .limit(batch_size)
                )
                entities = (await session.execute(entities_query)).scalars().all()

                # Assess each entity
                for entity in entities:
                    try:
                        assessment = await self.assess_entity(entity, session)
                        await self.store_assessment(assessment, entity, session)

                        # Update counts
                        status_key = assessment.quality_status.value
                        results[status_key] = results.get(status_key, 0) + 1
                        processed += 1

                    except Exception as e:
                        logger.error(f"Error assessing entity {entity.entity_id}: {e}")
                        results["errors"].append(f"Entity {entity.entity_id}: {str(e)}")

                offset += batch_size
                results["processed"] = processed

                logger.info(f"Processed {processed}/{total_count} entities")

            except Exception as e:
                logger.error(f"Error in batch assessment: {e}")
                results["errors"].append(f"Batch error: {str(e)}")
                break

        logger.info(
            f"Completed quality assessment: {processed}/{total_count} entities processed"
        )
        return results

    def _determine_quality_status(self, score: float) -> QualityStatus:
        """Determine quality status from score"""
        for status, threshold in self.quality_thresholds.items():
            if score >= threshold:
                return status
        return QualityStatus.CRITICAL

    def _determine_confidence_level(self, score: float) -> ConfidenceLevel:
        """Determine confidence level from score"""
        for level, threshold in self.confidence_thresholds.items():
            if score >= threshold:
                return level
        return ConfidenceLevel.VERY_LOW

    async def get_quality_summary(self, session: AsyncSession) -> Dict[str, Any]:
        """Get overall quality summary statistics"""
        # Quality status distribution
        status_query = (
            select(EntityRecord.quality_status, func.count(EntityRecord.id))
            .where(EntityRecord.is_active == True)
            .group_by(EntityRecord.quality_status)
        )
        status_results = (await session.execute(status_query)).all()
        status_distribution = {status: count for status, count in status_results}

        # Average scores by entity type
        scores_query = (
            select(
                EntityRecord.entity_type,
                func.avg(EntityRecord.overall_quality_score).label("avg_quality"),
                func.avg(EntityRecord.completeness_score).label("avg_completeness"),
                func.avg(EntityRecord.consistency_score).label("avg_consistency"),
                func.avg(EntityRecord.freshness_score).label("avg_freshness"),
                func.avg(EntityRecord.confidence_score).label("avg_confidence"),
                func.count(EntityRecord.id).label("count"),
            )
            .where(EntityRecord.is_active == True)
            .group_by(EntityRecord.entity_type)
        )
        scores_results = (await session.execute(scores_query)).all()

        entity_type_scores = {}
        for result in scores_results:
            entity_type_scores[result.entity_type] = {
                "average_quality": float(result.avg_quality or 0),
                "average_completeness": float(result.avg_completeness or 0),
                "average_consistency": float(result.avg_consistency or 0),
                "average_freshness": float(result.avg_freshness or 0),
                "average_confidence": float(result.avg_confidence or 0),
                "count": result.count,
            }

        # Recent issues
        issues_query = (
            select(EntityRecord.quality_issues, func.count(EntityRecord.id))
            .where(
                and_(
                    EntityRecord.is_active == True,
                    EntityRecord.has_issues == True,
                    EntityRecord.updated_at
                    >= datetime.now(timezone.utc) - timedelta(days=7),
                )
            )
            .group_by(EntityRecord.quality_issues)
            .limit(10)
        )

        return {
            "status_distribution": status_distribution,
            "entity_type_scores": entity_type_scores,
            "total_entities": sum(status_distribution.values()),
            "entities_with_issues": sum(
                1
                for status in status_distribution
                if status in [QualityStatus.POOR, QualityStatus.CRITICAL]
            ),
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }


# Global quality engine instance
quality_engine = DataQualityEngine()
